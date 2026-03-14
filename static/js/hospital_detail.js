// static/js/hospital_detail.js
const DAY_NAMES = { mon:'월', tue:'화', wed:'수', thu:'목', fri:'금', sat:'토', sun:'일' };
const TODAY_KEY = ['sun','mon','tue','wed','thu','fri','sat'][new Date().getDay()];

function statusClass(status) {
  return { open: 'status-open', upcoming: 'status-upcoming', closed: 'status-closed', unknown: 'status-closed' }[status] || 'status-closed';
}

function buildHoursTable(hours) {
  return `
    <table class="hours-table">
      ${Object.entries(hours).map(([key, val]) => `
        <tr class="${key === TODAY_KEY ? 'today' : ''}">
          <td>${DAY_NAMES[key]}</td>
          <td>${val}</td>
        </tr>
      `).join('')}
    </table>
  `;
}

function renderDetail(h) {
  const content = document.getElementById('detailContent');
  content.innerHTML = `
    <div class="detail-name">${h.name}</div>
    <div class="detail-depts">${h.departments.join(' · ')}</div>
    <span class="detail-status ${statusClass(h.status)}">${h.statusText}</span>

    <div class="detail-info-row">
      <span class="detail-info-label">주소</span>
      <span>${h.address}</span>
    </div>
    <div class="detail-info-row">
      <span class="detail-info-label">전화</span>
      <a href="tel:${h.phone}">${h.phone}</a>
    </div>
    <div class="detail-info-row" style="flex-direction:column;">
      <span class="detail-info-label" style="margin-bottom:4px;">운영시간</span>
      ${h.hours && Object.keys(h.hours).length > 0 ? buildHoursTable(h.hours) : '<span style="color:var(--color-text-sub);font-size:13px;">운영시간 정보 없음</span>'}
    </div>
  `;
}

function initDetailMap(hospital) {
  kakao.maps.load(() => {
    const container = document.getElementById('detailMap');
    const pos = new kakao.maps.LatLng(hospital.lat, hospital.lng);
    const map = new kakao.maps.Map(container, { center: pos, level: 3 });
    new kakao.maps.Marker({ map, position: pos, title: hospital.name });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const raw = sessionStorage.getItem('selectedHospital');
  const hospital = raw ? JSON.parse(raw) : null;

  if (!hospital) {
    document.getElementById('detailContent').innerHTML =
      '<div style="color:var(--color-closed);">병원 정보를 찾을 수 없습니다. 목록으로 돌아가 다시 선택해 주세요.</div>';
    return;
  }

  renderDetail(hospital);

  if (KAKAO_JS_API_KEY) {
    initDetailMap(hospital);
  }
});
