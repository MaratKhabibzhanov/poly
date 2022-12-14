from django.contrib.auth import get_user
from django.db.utils import InternalError
from django.db import connections, connection, models
from django.http import HttpResponse
from psycopg2 import sql
import re



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
                context = dictfetchall(cursor)
                return context
            elif operation == ('insert' or 'delete'):
                context = cursor.fetchone()[0]
                return context
        except InternalError as err:
            context = str(err).split('\n')[0]
            HttpResponse(context)


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


def insert(request, table_name: str, column: tuple, value: tuple, returning: str=None):
    query = "INSERT INTO {table_name} ({columns}) VALUES ({values}) "
    columns = sql.SQL(',').join(map(sql.Identifier, column))
    values = sql.SQL(',').join(map(sql.Literal, value))
    if returning:
        query += "RETURNING {returning}"
    stmt = sql.SQL(query).format(table_name=sql.Identifier(table_name),
                                 columns=columns,
                                 values=values,
                                 returning=sql.Identifier(returning) if returning else None,
                                 )
    return connect_db(request, stmt, operation='insert' if returning else None)


def delete(request, table_name: str, where_col: tuple, where_val: tuple, returning: str=None):
    query = "DELETE FROM {table_name} WHERE {where} "
    where_list = [sql.SQL('{} = {}').format(sql.Identifier(k), sql.Literal(v)) for k, v in zip(where_col, where_val)]
    where_sql = sql.SQL(' AND ').join(where_list)
    if returning:
        query += "RETURNING {returning}"
    stmt = sql.SQL(query).format(table_name=sql.Identifier(table_name),
                                 where=where_sql,
                                 returning=sql.Identifier(returning) if returning else None,
                                 )
    return connect_db(request, stmt, operation='delete' if returning else None)


def get_group(request):
    user = get_user(request)
    group = 'doctor' if user.groups.filter(name='Доктор').exists() else 'default'
    return group

# def crud_treatment(request, card_no=None, id=None):
#     from poly_crud.form import TreatmentForm
#     if id:
#         data = select(request=request, table_name='treatment', where_col=('id',), where_val=(id,))[0]
#         drag = select(request, table_name='drag', join_table=('treatment_has_drag', ), join_ids=(('id_drag', 'id'),),
#                         select_column=('id', ), where_col=('id_treatment',), where_val=(id,))
#         data['treatment_drag'] = [dic['id'] for dic in drag]
#     elif card_no:
#         data = {'card_no_patient': card_no}
#     if request.method == 'POST':
#         if id:
#             if request.POST.get('action') == 'Delete':
#                 card_no = delete(request, table_name='treatment', where_col=('id',),
#                                  where_val=(id,), returning='card_no_patient')
#                 # if re.match('[А-Я]{2}\d{4}[А-Я]{1}', card_no):
#                 #     return {'card_no': card_no}
#                 # else:
#                 #     return card_no
#                 return {'card_no': card_no}
#         form = TreatmentForm(request.POST, request=request)
#         if form.is_valid():
#             clean_data = form.cleaned_data
#             form_data = (clean_data.get('date_in'), clean_data.get('date_out'), clean_data.get('diagnosis'),
#                          clean_data.get('symptom'), clean_data.get('id_doctor').id,
#                          clean_data.get('card_no_patient').card_no)
#             form_drag = [drag.id for drag in clean_data.get('treatment_drag')]
#             columns = ('date_in', 'date_out', 'diagnosis', 'symptom', 'id_doctor', 'card_no_patient')
#             if id:
#                 update(request, 'treatment', columns, form_data, ('id',), (id,))
#                 table_drag = select(request, 'treatment_has_drag', select_column=('id_drag',),
#                                   where_col=('id_treatment',), where_val=(id, ))
#                 table_drag = [drag['id_drag'] for drag in table_drag]
#                 for drag in form_drag:
#                     if drag not in table_drag:
#                         insert(request, 'treatment_has_drag', ('id_treatment', 'id_drag'), (id, drag))
#                     else:
#                         table_drag.remove(drag)
#                 for drag in table_drag:
#                     delete(request, 'treatment_has_drag', ('id_treatment', 'id_drag'), (id, drag))
#                 card_no = form_data[-1]
#             elif card_no:
#                 id = insert(request, 'treatment', columns, form_data, returning='id')
#                 for drag in clean_data.get('treatment_drag'):
#                     insert(request, 'treatment_has_drag', ('id_treatment', 'id_drag'), (id, drag.id))
#             context = {'card_no': card_no}
#             return context
#     else:
#         form = TreatmentForm(data, request=request)
#     context = {'form': form}
#     return context
