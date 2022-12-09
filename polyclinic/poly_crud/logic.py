from django.contrib.auth import get_user
from django.db.utils import InternalError
from django.db import connections, connection, models
from django.http import HttpResponse
from psycopg2 import sql

from poly_crud.models import Doctor, Treatment, Patient, Drag


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def connect_db(request, stmt, operation='select'):
    with connections[get_group(request)].cursor() as cursor:
        try:
            cursor.execute(stmt)
            if operation == 'select':
                result = dictfetchall(cursor)
                return result
            elif operation == 'insert':
                id = cursor.fetchone()[0]
                return id
        except InternalError as err:
            error = str(err).split('\n')[0]
            return error


def select(request, table_name: str, select_column: tuple=None, join_table: tuple=None, join_ids: tuple=None,
           where_col: tuple=None, where_val: tuple=None, order_by: str=None, desc: bool=None, limit: int=None):
    query = "SELECT * FROM {table_name} "
    if select_column:
        query = "SELECT {select_column} FROM {table_name} "
    if join_table:
        query += "{join} "
        prev_table = table_name
        join_sql = sql.SQL('')
        for table, (j_pk, p_pk) in zip(join_table, join_ids):
            join_sql += sql.SQL("JOIN {join_table} ON {join_table}.{j_pk} = {prev_table}.{p_pk} ").format(
                join_table=sql.Identifier(table),
                prev_table=sql.Identifier(prev_table),
                p_pk=sql.Identifier(p_pk),
                j_pk=sql.Identifier(j_pk),
            )
            prev_table = table
    if where_val:
        query += "WHERE {where} "
        where_zip = zip(where_col, where_val)
        where_list = [sql.SQL('{} = {}').format(sql.Identifier(k), sql.Literal(v)) for k, v in where_zip]
        where_sql = sql.SQL(' AND ').join(where_list)
    if order_by:
        query += "ORDER BY {order_by} "
        if desc:
            query += "DESC "
    if limit:
        query += "LIMIT {limit} "
    stmt = sql.SQL(query).format(select_column=sql.SQL(',').join(map(sql.Identifier, select_column))
                                                if select_column else None,
                                 table_name=sql.Identifier(table_name),
                                 order_by=sql.Identifier(order_by) if order_by else None,
                                 where=where_sql if where_val else None,
                                 join=join_sql if join_table else None,
                                 limit=sql.Literal(limit) if limit else None,
                                 )
    return connect_db(request, stmt)


def update(request, table_name: str, column: tuple, value: tuple, where_col: tuple, where_val: tuple):
    query = "UPDATE {table_name} SET ({columns}) = ({values}) WHERE {where};"
    where_list = [sql.SQL('{} = {}').format(sql.Identifier(k), sql.Literal(v)) for k, v in zip(where_col, where_val)]
    where_sql = sql.SQL(' AND ').join(where_list)
    stmt = sql.SQL(query).format(table_name=sql.Identifier(table_name),
                                 columns=sql.SQL(',').join(map(sql.Identifier, column)),
                                 values=sql.SQL(',').join(map(sql.Literal, value)),
                                 where=where_sql,
                                 )
    return connect_db(request, stmt, operation='update')


def insert(request, table_name: str, column: tuple, value: tuple):
    query = "INSERT INTO {table_name} ({columns}) VALUES ({values}) RETURNING id;"
    columns = sql.SQL(',').join(map(sql.Identifier, column))
    values = sql.SQL(',').join(map(sql.Literal, value))
    stmt = sql.SQL(query).format(table_name=sql.Identifier(table_name),
                                 columns=columns,
                                 values=values,
                                 )
    return connect_db(request, stmt, operation='insert')


def delete(request, table_name: str, where_col: tuple, where_val: tuple):
    query = "DELETE FROM {table_name} WHERE {where};"
    where_list = [sql.SQL('{} = {}').format(sql.Identifier(k), sql.Literal(v)) for k, v in zip(where_col, where_val)]
    where_sql = sql.SQL(' AND ').join(where_list)
    stmt = sql.SQL(query).format(table_name=sql.Identifier(table_name),
                                 where=where_sql,
                                 )
    return connect_db(request, stmt, operation='delete')


def get_group(request):
    user = get_user(request)
    group = 'doctor' if user.groups.filter(name='Доктор').exists() else 'default'
    return group

def crud_treatment(request, card_no=None, id=None, group='default'):
    from poly_crud.form import TreatmentForm

    if id:
        treatment = Treatment.objects.using(group).raw("SELECT * FROM treatment WHERE id = %s;", [id])[0]
        # data = select(request=request, table_name='treatment', where_col=('id',), where_val=(id,))[0]
        with connections[group].cursor() as cursor:
            try:
                cursor.execute("SELECT d.id "
                                "FROM drag AS d "
                                "JOIN treatment_has_drag AS td ON td.id_drag = d.id "
                                "WHERE td.id_treatment = %s;", [id, ])
                drag = [row[0] for row in cursor.fetchall()]
                print(f'old = {drag}')
            except InternalError as err:
                error = str(err).split('\n')[0]
                return error
        # drag = select(request, table_name='drag', join_table=('treatment_has_drag', ), join_ids=(('id_drag', 'id'),),
        #          select_column=('id', ), where_col=('id_treatment',), where_val=(id,))
        # print(drag)
        # data['treatment_drag'] = [dic['id'] for dic in drag]
        data = {'id': treatment.get("id"),
                'date_in': treatment.get("date_in"),
                'date_out': treatment.get("date_out"),
                'diagnosis': treatment.get("diagnosis"),
                'symptom': treatment.get("symptom"),
                'id_doctor': treatment.get("id_doctor"),
                'card_no_patient': treatment.get("card_no_patient"),
                'treatment_drag': drag,
                }
    elif card_no:
        data = {'card_no_patient': card_no}

    if request.method == 'POST':
        if id:
            if request.POST.get('action') == 'Delete':
                with connections[group].cursor() as cursor:
                    try:
                        cursor.execute("SELECT card_no_patient FROM treatment WHERE id = %s;", [id, ])
                        card_no = cursor.fetchone()[0]
                        cursor.execute("DELETE FROM treatment WHERE id = %s;", [id, ])
                        context = {'card_no': card_no}
                        return context
                    except InternalError as err:
                        error = str(err).split('\n')[0]
                        return error

        form = TreatmentForm(request.POST, request=request)
        if form.is_valid():
            clean_data = form.cleaned_data
            form_data = (clean_data.get('date_in'), clean_data.get('date_out'), clean_data.get('diagnosis'),
                         clean_data.get('symptom'), clean_data.get('id_doctor').id,
                         clean_data.get('card_no_patient').card_no)
            if id:
                clean_drag = [drag.id for drag in clean_data.get('treatment_drag')]
            with connections[group].cursor() as cursor:
                try:
                    if id:
                        cursor.execute("UPDATE treatment "
                                       "SET (date_in, date_out, diagnosis, symptom, id_doctor, card_no_patient) = %s "
                                       "WHERE id = %s;", [form_data, id])
                        for drag in clean_data['treatment_drag']:
                            cursor.execute("SELECT * FROM treatment_has_drag AS tg "
                                           "WHERE tg.id_treatment = %s AND tg.id_drag = %s;", [id, drag.id])
                            presense = cursor.fetchone()
                            if not presense:
                                cursor.execute("INSERT INTO treatment_has_drag VALUES %s;", [(id, drag.id), ])
                        cursor.execute("SELECT tg.id_drag FROM treatment_has_drag AS tg "
                                       "WHERE tg.id_treatment = %s;", [id, ])
                        id_drag = cursor.fetchall()
                        for drag in id_drag:
                            if drag[0] not in clean_drag:
                                cursor.execute("DELETE FROM treatment_has_drag "
                                               "WHERE id_treatment = %s AND id_drag = %s;", [id, drag])
                        cursor.execute("SELECT card_no_patient FROM treatment WHERE id = %s;", [id, ])
                        card_no = cursor.fetchone()[0]
                    elif card_no:
                        cursor.execute("INSERT INTO treatment "
                                       "(date_in, date_out, diagnosis, symptom, id_doctor, card_no_patient) "
                                       "VALUES %s RETURNING id;", [form_data, ])
                        id = cursor.fetchone()[0]
                        for drag in clean_data.get('treatment_drag'):
                            cursor.execute("INSERT INTO treatment_has_drag VALUES %s;", [(id, drag.id),])
                    context = {'card_no': card_no}
                    return context
                except InternalError as err:
                    error = str(err).split('\n')[0]
                    return error
    else:
        form = TreatmentForm(data, request=request)
    context = {'form': form}
    return context
