from prettytable import PrettyTable

th = ['ФИО', 'Отметка']
td = ['Воробьева Мария', '*',
      'Селин Артём', 'н',
      'Лопатин Егор', 'н',
      'Кочина Виктория', '*',
      'Мишин Алексей', '*']

columns = len(th)
table = PrettyTable(th)
td_data = td[:]
while td_data:
    table.add_row(td_data[:columns])
    td_data = td_data[columns:]

print(str(table), type(table))  # Печатаем таблицу
