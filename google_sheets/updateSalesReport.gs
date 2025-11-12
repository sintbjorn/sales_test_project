/**
 * updateSalesReport.gs — Google Apps Script
 * Автор: <Ваше Имя>
 * Короткая человеческая заметка:
 *  Я оставил простую, но воспроизводимую логику: мок-данные превращаем в суммы,
 *  раскладываем по датам и делаем сводку. Порог для письма можно менять.
 */
function updateSalesReport() {
  const ALERT_EMAIL = "you@example.com"; // <-- УКАЖИТЕ свой email
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const raw = ss.getSheetByName("Raw Data") || ss.insertSheet("Raw Data");
  const summary = ss.getSheetByName("Summary") || ss.insertSheet("Summary");

  // 1) Внешние данные (мок)
  const url = "https://jsonplaceholder.typicode.com/posts";
  const resp = UrlFetchApp.fetch(url, { "muteHttpExceptions": true });
  const code = resp.getResponseCode();
  if (code !== 200) {
    throw new Error("Upstream error: " + code + " " + resp.getContentText().slice(0,200));
  }
  const data = JSON.parse(resp.getContentText()); // массив объектов

  // 2) Запись в Raw Data
  raw.clear();
  raw.getRange(1,1,1,5).setValues([["id","title","body","amount","date"]]);

  const today = new Date();
  const rows = data.map(p => {
    const amount = (p.title ? p.title.length : 0) + (p.body ? p.body.length : 0);
    const d = new Date(today);
    d.setDate(today.getDate() - (p.id % 14)); // немного «гуляем» по датам
    return [p.id, p.title, p.body, amount, d];
  });
  if (rows.length) raw.getRange(2,1,rows.length,5).setValues(rows);

  // 3) Сводка в Summary: сумма по датам
  summary.clear();
  summary.getRange(1,1,1,2).setValues([["date","total_amount"]]);

  const map = {};
  rows.forEach(r => {
    const d = Utilities.formatDate(new Date(r[4]), Session.getScriptTimeZone(), "yyyy-MM-dd");
    map[d] = (map[d] || 0) + r[3];
  });
  const dates = Object.keys(map).sort();
  const sumRows = dates.map(d => [d, map[d]]);
  if (sumRows.length) summary.getRange(2,1,sumRows.length,2).setValues(sumRows);

  // 4) Пороговое письмо
  const total = sumRows.reduce((acc, r) => acc + r[1], 0);
  if (total > 10000) {
    MailApp.sendEmail({
      to: ALERT_EMAIL,
      subject: "Sales Alert: total > 10000",
      htmlBody: "Общая сумма продаж: <b>" + total + "</b>"
    });
  }
}
