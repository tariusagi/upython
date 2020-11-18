#!/usr/bin/python3
# vim: set filetype=python :
from datetime import datetime

class Ansi:
	''' Returns ANSI color encoded string'''
	def black(text, blink = False):
		return "\033[0;30m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

	def red(text, blink = False):
		return "\033[0;31m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

	def green(text, blink = False):
		return "\033[0;32m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

	def yellow(text, blink = False):
		return "\033[0;33m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

	def blue(text, blink = False):
		return "\033[0;34m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

	def purple(text, blink = False):
		return "\033[0;35m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

	def cyan(text, blink = False):
		return "\033[0;36m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

	def lgray(text, blink = False):
		return "\033[0;37m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

	def dgray(text, blink = False):
		return "\033[1;30m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

	def lred(text, blink = False):
		return "\033[1;31m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

	def lgreen(text, blink = False):
		return "\033[1;32m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

	def lyellow(text, blink = False):
		return "\033[1;33m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

	def lblue(text, blink = False):
		return "\033[1;34m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

	def lpurple(text, blink = False):
		return "\033[1;35m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

	def lcyan(text, blink = False):
		return "\033[1;36m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

	def lwhite(text, blink = False):
		return "\033[1;37m" + ("\033[5m" if blink else '') + str(text) + "\033[0m"

class UziSql:
	def quote(args):
		"""Surround given "args" with backticks. Identifiers can be a
		single string, a tuple, or a list. Return value is a quoted list.
		"""
		if isinstance(args, str):
			return f'`{args.strip()}`'
		elif isinstance(args, (tuple, list)):
			r = []
			for i in range(len(args)):
				r.append(f'`{str(args[i]).strip()}`')
			return r
		else:
			# Raise exception for unsupported arguments.
			raise TypeError(f'Argument type {type(args)} is not supported')

	def escape(value):
		"""Escape given value into proper SQL syntax (sing-quotes
		text, convert date & time into SQL format...). "v" can be a number,
		a string, or a date/time. Return value is the escaped one. NOTE: None
		value will be returned as Null.
		"""
		if value is None:
			return 'NULL'
		elif isinstance(value, (int, float)):
			# For number, return as a string.
			return str(value)
		elif isinstance(value, str):
			# For text, return single-quoted string.
			return f"'{value.strip()}'"
		elif isinstance(value, datetime):
			# For date & time, return MySQL date formatted string.
			return "'" + value.strftime('%Y-%m-%d %H:%M:%S') + "'"
		else:
			# Raise exception for unsupported arguments.
			raise TypeError(f'Argument type {type(value)} is not supported')

	def escape_all(values):
		"""Escape given "values" into proper SQL syntax (sing-quotes text, 
		convert date & time into SQL format...). "args" can be a number, a 
		string, a tuple, or a list. Return value(s) is the escaped values.
		"""
		if isinstance(values, (int, float, datetime)):
			return UziSql.escape(values)
		elif isinstance(values, (tuple, list)):
			r = []
			for i in range(len(values)):
				r.append(UziSql.escape(values[i]))
			return r
		else:
			# Raise exception for unsupported arguments.
			raise TypeError(f'Argument type {type(values)} is not supported')

	def select(table, columns, filters = None, groups = None, having = None, 
		order = None, limit = None):
		"""Build a query to select rows from a table. Arguments are:
		- columns: a tuple of selected columns names.
		- filters: a dict of "column = value" pairs. Currently support only
		inclusive equal conditions. TODO: support more complex conditions.
		- groups: a tuple of columns names to group by.
		- having: SQL statement after "HAVING".
		- order: a tuple of columns names to order the result set.
		- limit: a integer to limit the number of returned rows. 
		Example: the following call query from table "user_profile" any row that
		have column "sex" is 'M' and year of birth is less than the value in the
		(Python) variable 'year'. The result set is not grouped, but will be
		ordered by sex, then name, and limit to a maximum of 10 rows:
			r = connector.execute(UziSql.select(
				table = 'user_profile',
				columns = ('name', 'sex', 'birthday'),
				filters = dict(sex = 'M'),
				group = None,
				having = None,
				order = ('sex', 'name'),
				limit = 10
			))
		"""
		# Quote identifiers.
		table = UziSql.quote(table)
		if not isinstance(columns, (tuple, list)):
			raise TypeError('columns must be a tuple or list')
		elif len(columns) == 0:
			raise ValueError('columns list cannot be empty')
		columns = ', '.join(UziSql.quote(columns))
		# Build the WHERE clause.
		where = ''
		if filters is not None:
			if not isinstance(filters, dict):
				raise TypeError('Filters must be a dict')
			else:
				for c in filters:
					v = UziSql.escape(filters[c])
					c = UziSql.quote(c)
					if where == '':
						where = f"WHERE {c} = {v}"
					else:
						where += f" AND {c} = {v}"
		# Build the GROUP BY clause.
		group_by = ''
		if groups is not None:
			if not isinstance(groups, tuple):
				raise TypeError('groups must be a tuple')
			else:
				for c in groups:
					c = UziSql.quote(c)
					if group_by == '':
						group_by = f"GROUP BY {c}"
					else:
						group_by += f", {c}"
		# Build HAVING clause.
		if having is None:
			having = ''
		else:
			having = f'HAVING {having}'
		# Build ORDER BY clause.
		order_by = ''
		if order is not None:
			if not isinstance(order, tuple):
				raise TypeError('order must be a tuple')
			else:
				for c in order:
					c = UziSql.quote(c)
					if order_by == '':
						order_by = f"ORDER BY {c}"
					else:
						order_by += f", {c}"
		# Build LIMIT clause.
		limit_clause = ''
		if limit is not None:
			if not isinstance(limit, int):
				raise TypeError('limit must be an int')
			else:
				limit_clause = " LIMIT {limit}"
		# Now return the whole query.
		return f'SELECT {columns} FROM {table} {where} {group_by} {having} {order_by} {limit_clause}'.strip()

	def insert(table, columns):
		"""Build a query to insert a single row into a table. Arguments are:
		- table: the table name.
		- columns: a dict of "column = value" pairs.
		Example: the following calll insert new user profiles into the 
		user_profile table, and on duplicated key (name), the sex and birthday 
		columns will be updated:
			r = connector.execute(UziSql.insert(
				table = 'user_profile',
				columns = dict(
					name = mickey.name,
					sex = mickey.sex,
					birthday = mickey.birthday
				)
			))
		"""
		table = UziSql.quote(table)
		# Build columns list.
		col_sql = ''
		val_sql = ''
		if not isinstance(columns, dict):
			raise TypeError('columns must be a dict')
		elif len(columns) == 0:
			raise ValueError('columns list cannot be empty')
		else:
			for c in columns:
				if col_sql == '':
					col_sql += '(' + UziSql.quote(c)
					val_sql += '(' + UziSql.escape(columns[c])
				else:
					col_sql += ', ' + UziSql.quote(c)
					val_sql += ', ' + UziSql.escape(columns[c])
			col_sql += ')'
			val_sql += ')'
		# Now return the whole query.
		return f'INSERT INTO {table}{col_sql} VALUES {val_sql}'

	def update(table, columns, filters = None, order = None, limit = None):
		"""Build a query to update a table. Arguments are:
		- table: table name.
		- columns: a dict of columns names and values pairs.
		- filters: a dict of conditions (column = value) pairs.
		Example: the following call update Mickey's sex and birthday by match
		his name:
			r = connector.execute(UziSql.update(
				table = 'user_profile',
				columns = dict(
					sex = mickey.sex,
					birthday = mickey.birthday
				),
				filters = dict(name = mickey.name)
			))
		"""
		# Quote identifiers.
		table = UziSql.quote(table)
		# Build columns assignment list.
		if not isinstance(columns, dict):
			raise TypeError('columns must be a dict')
		elif len(columns) == 0:
			raise ValueError('columns assignment cannot be empty')
		else:
			assignment = ''
			for c in columns:
				if assignment == '':
					assignment += 'SET ' + UziSql.quote(c) + ' = ' + UziSql.escape(columns[c])
				else:
					assignment += ', ' + UziSql.quote(c) + ' = ' + UziSql.escape(columns[c])
		# Build the WHERE clause.
		where = ''
		if filters is not None:
			if not isinstance(filters, dict):
				raise TypeError('Filters must be a dict')
			else:
				for c in filters:
					v = UziSql.escape(filters[c])
					c = UziSql.quote(c)
					if where == '':
						where = f"WHERE {c} = {v}"
					else:
						where += f" AND {c} = {v}"
		# Build ORDER BY clause.
		order_by = ''
		if order is not None:
			if not isinstance(order, tuple):
				raise TypeError('order must be a tuple')
			else:
				for c in order:
					c = UziSql.quote(c)
					if order_by == '':
						order_by = f"ORDER BY {c}"
					else:
						order_by += f", {c}"
		# Build LIMIT clause.
		limit_clause = ''
		if limit is not None:
			if not isinstance(limit, int):
				raise TypeError('limit must be an int')
			else:
				limit_clause = " LIMIT {limit}"
		# Now return the whole query.
		return f'UPDATE {table} {assignment} {where} {order_by} {limit_clause}'.strip()

	def delete(table, filters = None, order = None, limit = None):
		"""Build a query to delete rows from a table". Arguments are:
		- table: table name.
		- filters: a dict of conditions (column = value) pairs.
		- order: a tuple of columns names to order the result set.
		- limit: a integer to limit the number of returned rows. 
		Example: the following call delete a maximum of 10 rows from
		"user_profile" table that is female.
			r = connector.execute(UziSql.delete(
				table = 'user_profile',
				filters = dict(
					sex = 'F',
					age = 18
				),
				limit = 10
			))
		"""
		# Quote identifiers.
		table = UziSql.quote(table)
		# Build the WHERE clause.
		where = ''
		if filters is not None:
			if not isinstance(filters, dict):
				raise TypeError('Filters must be a dict')
			else:
				for c in filters:
					v = UziSql.escape(filters[c])
					c = UziSql.quote(c)
					if where == '':
						where = f"WHERE {c} = {v}"
					else:
						where += f" AND {c} = {v}"
		# Build ORDER BY clause.
		order_by = ''
		if order is not None:
			if not isinstance(order, tuple):
				raise TypeError('order must be a tuple')
			else:
				for c in order:
					c = UziSql.quote(c)
					if order_by == '':
						order_by = f"ORDER BY {c}"
					else:
						order_by += f", {c}"
		# Build LIMIT clause.
		limit_clause = ''
		if limit is not None:
			if not isinstance(limit, int):
				raise TypeError('limit must be an int')
			else:
				limit_clause = " LIMIT {limit}"
		# Now return the whole query.
		return f'DELETE FROM {table} {where} {order_by} {limit_clause}'.strip()
