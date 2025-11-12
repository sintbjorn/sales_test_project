# Google Sheets — инструкции

## Структура листа Sales (пример)
Предположим, на листе **Sales** есть колонки:
- A: Date
- B: Product
- C: Category
- D: Quantity
- E: Price

В ячейке `Sales!H1` — начало периода (StartDate), в `Sales!H2` — конец (EndDate).

### 1) Группировка сумм по категориям с фильтром по датам (Summary!A1)
```
=QUERY(
  Sales!A:E,
  "select C, sum(D*E)
   where A >= date '" & TEXT(Sales!H1, "yyyy-mm-dd") & "'
     and A <= date '" & TEXT(Sales!H2, "yyyy-mm-dd") & "'
   group by C
   label sum(D*E) 'Total'",
  1
)
```

### 2) ARRAYFORMULA для произведения количества на цену (Sales!F1)
```
=ARRAYFORMULA(
  IF(ROW(D:D)=1, "Line Total",
    IF(LEN(D:D), D:D * E:E, )
  )
)
```

### 3) Процент от общей суммы (Sales!G1, если Line Total в F)
```
=ARRAYFORMULA(
  IF(ROW(F:F)=1, "% of Total",
    IF(LEN(F:F),
      F:F / SUM(F:F),
    )
  )
)
```

## Apps Script
В редакторе Extensions → Apps Script создайте файл и вставьте `updateSalesReport.gs` из этого проекта.
Заполните email получателя в константе `ALERT_EMAIL`. Запустите `updateSalesReport`.
