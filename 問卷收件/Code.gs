/**
 * 集思室內裝修｜需求問卷收件程式（Google Apps Script）
 * 把這整份貼到「試算表 → 擴充功能 → Apps Script」的 Code.gs，再部署成「網頁應用程式」。
 * 設定步驟請看同資料夾的「設定教學.md」。
 */

// 收到新問卷時寄通知信到這個信箱；留空 '' 則不寄
const NOTIFY_EMAIL = '';

// 客戶上傳的風格照片會存到雲端硬碟這個資料夾（不存在會自動建立）
const PHOTO_FOLDER_NAME = '集思需求問卷_風格照片';

const SHEET_NAME = '問卷回覆';

// 試算表欄位順序（需與問卷欄位名稱一致）
const HEADERS = [
  '填寫時間', '姓名', '手機', 'LINE ID',
  '地址', '社區', '屋齡', '房屋類型', '權狀坪數', '室內實坪',
  '裝修範圍', '局部空間',
  '交屋日', '希望入住日', '客變',
  '預算',
  '居住人數', '成員年齡', '寵物', '未來5年變化', '家庭變化補充',
  '喜歡風格', '風格照片', '參考連結', '不喜歡的元素',
  '主要決策者', '比較其他公司',
  '來源', '來源補充', '其他備註',
];

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const data = JSON.parse(e.postData.contents);
    const sheet = getSheet_();

    // 照片：存到雲端硬碟，試算表放連結
    const photos = Array.isArray(data._photos) ? data._photos.slice(0, 5) : [];
    if (photos.length) {
      const folder = getFolder_();
      const who = (data['姓名'] || '客戶') + '_' + Utilities.formatDate(new Date(), 'Asia/Taipei', 'yyyyMMdd-HHmm');
      const links = photos.map(function (p, i) {
        const blob = Utilities.newBlob(Utilities.base64Decode(p.data), p.type || 'image/jpeg', who + '_' + (i + 1) + '.jpg');
        return folder.createFile(blob).getUrl();
      });
      data['風格照片'] = links.join('\n');
    }

    data['填寫時間'] = Utilities.formatDate(new Date(), 'Asia/Taipei', 'yyyy-MM-dd HH:mm:ss');
    const row = HEADERS.map(function (h) { return data[h] == null ? '' : String(data[h]); });
    // 電話、日期等以文字存入，避免 09 開頭被吃掉
    sheet.appendRow(row.map(function (v) { return /^[0-9+\-]/.test(v) ? "'" + v : v; }));

    if (NOTIFY_EMAIL) {
      const body = HEADERS.filter(function (h, i) { return row[i]; })
        .map(function (h) { return h + '：' + data[h]; }).join('\n');
      MailApp.sendEmail(NOTIFY_EMAIL, '【新問卷】' + (data['姓名'] || '') + '｜' + (data['預算'] || ''), body);
    }

    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

// 用瀏覽器打開網址時顯示，方便確認部署成功
function doGet() {
  return json_({ ok: true, message: '問卷收件程式運作中' });
}

function getSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) sheet = ss.insertSheet(SHEET_NAME);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold').setBackground('#f3ecdc');
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function getFolder_() {
  const it = DriveApp.getFoldersByName(PHOTO_FOLDER_NAME);
  return it.hasNext() ? it.next() : DriveApp.createFolder(PHOTO_FOLDER_NAME);
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

// 在 Apps Script 編輯器手動執行一次，用來授權並測試寫入
function testWrite() {
  doPost({ postData: { contents: JSON.stringify({ '姓名': '測試資料（可刪除）', '手機': '0912345678', '預算': '100 萬以下' }) } });
}
