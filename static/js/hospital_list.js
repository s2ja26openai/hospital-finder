// static/js/hospital_list.js
let currentRadius = 500;
let currentSort = 'score';
let kakaoMap = null;
let markers = [];

function setRadius(btn) {
  document.querySelectorAll('.radius-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  currentRadius = parseInt(btn.dataset.radius);
  renderList();
}

function setSort(btn) {
  document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  currentSort = btn.dataset.sort;
  renderList();
}

function filterAndSort(hospitals) {
  let filtered = hospitals.filter(h => h.distance <= currentRadius);
  if (SELECTED_DEPARTMENT) {
    filtered = filtered.filter(h => h.departments.includes(SELECTED_DEPARTMENT));
  }
  if (currentSort === 'score') {
    filtered.sort((a, b) => {
      const statusOrder = { open: 0, upcoming: 1, closed: 2 };
      if (statusOrder[a.status] !== statusOrder[b.status]) {
        return statusOrder[a.status] - statusOrder[b.status];
      }
      return b.score - a.score;
    });
  } else {
    filtered.sort((a, b) => a.distance - b.distance);
  }
  return filtered;
}

function statusClass(status) {
  return { open: 'status-open', upcoming: 'status-upcoming', closed: 'status-closed' }[status];
}

function renderList() {
  const list = document.getElementById('hospitalList');
  const summary = document.getElementById('listSummary');
  const filtered = filterAndSort(window.MOCK_HOSPITALS);

  summary.textContent = `${filtered.length}개 병원`;
  list.innerHTML = '';

  if (filtered.length === 0) {
    list.innerHTML = '<div style="padding:40px;text-align:center;color:var(--color-text-sub);">해당 반경 내 병원이 없습니다.</div>';
    return;
  }

  filtered.forEach(h => {
    const card = document.createElement('div');
    card.className = 'hospital-card';
    card.dataset.id = h.id;
    card.innerHTML = `
      <div class="card-header">
        <span class="card-name">${h.name}</span>
        <span class="card-distance">${h.distance >= 1000 ? (h.distance/1000).toFixed(1)+'km' : h.distance+'m'}</span>
      </div>
      <div class="card-depts">${h.departments.join(' · ')}</div>
      <span class="card-status ${statusClass(h.status)}">${h.statusText}</span>
      <div class="card-review">${h.reviewSummary}</div>
    `;
    card.onclick = () => openDetail(h);
    list.appendChild(card);
  });

  updateMapMarkers(filtered);
}

function openDetail(hospital) {
  document.querySelectorAll('.hospital-card').forEach(c => c.classList.remove('selected'));
  const card = document.querySelector(`.hospital-card[data-id="${hospital.id}"]`);
  if (card) card.classList.add('selected');

  if (kakaoMap) {
    const pos = new kakao.maps.LatLng(hospital.lat, hospital.lng);
    kakaoMap.setCenter(pos);
  }

  window.location.href = `/hospitals/${hospital.id}`;
}

function initMap() {
  kakao.maps.load(() => {
    const container = document.getElementById('kakaoMap');
    const lat = window.LocationState ? window.LocationState.lat : 37.5665;
    const lng = window.LocationState ? window.LocationState.lng : 126.9780;
    kakaoMap = new kakao.maps.Map(container, {
      center: new kakao.maps.LatLng(lat, lng),
      level: 4
    });
    renderList();
  });
}

function updateMapMarkers(hospitals) {
  markers.forEach(m => m.setMap(null));
  markers = [];
  if (!kakaoMap) return;

  hospitals.forEach(h => {
    const marker = new kakao.maps.Marker({
      map: kakaoMap,
      position: new kakao.maps.LatLng(h.lat, h.lng),
      title: h.name
    });
    markers.push(marker);
  });
}

window.onLocationSet = () => renderList();

document.addEventListener('DOMContentLoaded', () => {
  if (KAKAO_JS_API_KEY && KAKAO_JS_API_KEY !== '') {
    initMap();
  } else {
    renderList();
  }
});
