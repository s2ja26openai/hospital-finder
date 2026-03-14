// static/js/hospital_list.js
let currentRadius = 500;
let currentSort = 'score';
let kakaoMap = null;
let markers = [];

function setRadius(btn) {
  document.querySelectorAll('.radius-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  currentRadius = parseInt(btn.dataset.radius);
  loadHospitals();
}

function setSort(btn) {
  document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  currentSort = btn.dataset.sort;
  loadHospitals();
}

function statusClass(status) {
  return {
    open: 'status-open',
    upcoming: 'status-upcoming',
    closed: 'status-closed',
    unknown: 'status-closed',
  }[status] || 'status-closed';
}

async function loadHospitals() {
  const { lat, lng } = window.LocationState;
  if (!lat || !lng) return;

  const list = document.getElementById('hospitalList');
  const summary = document.getElementById('listSummary');
  list.innerHTML = '<div style="padding:40px;text-align:center;color:var(--color-text-sub);">불러오는 중...</div>';

  const params = new URLSearchParams({
    lat, lng,
    radius: currentRadius,
    department: SELECTED_DEPARTMENT || '',
    sort: currentSort,
  });

  try {
    const res = await fetch(`/api/hospitals?${params}`);
    const data = await res.json();
    const hospitals = data.hospitals || [];

    summary.textContent = `${data.total}개 병원`;
    renderHospitalList(hospitals);
    updateMapMarkers(hospitals);
  } catch (e) {
    list.innerHTML = '<div style="padding:40px;text-align:center;color:var(--color-text-sub);">병원 정보를 불러오지 못했습니다.</div>';
  }
}

function renderHospitalList(hospitals) {
  const list = document.getElementById('hospitalList');
  list.innerHTML = '';

  if (hospitals.length === 0) {
    list.innerHTML = '<div style="padding:40px;text-align:center;color:var(--color-text-sub);">해당 반경 내 병원이 없습니다.</div>';
    return;
  }

  hospitals.forEach(h => {
    const card = document.createElement('div');
    card.className = 'hospital-card';
    card.dataset.id = h.id;
    const distLabel = h.distance >= 1000 ? (h.distance / 1000).toFixed(1) + 'km' : h.distance + 'm';
    card.innerHTML = `
      <div class="card-header">
        <span class="card-name">${h.name}</span>
        <span class="card-distance">${distLabel}</span>
      </div>
      <div class="card-depts">${h.departments.join(' · ')}</div>
      <span class="card-status ${statusClass(h.status)}">${h.statusText}</span>
      ${h.reviewSummary ? `<div class="card-review">${h.reviewSummary}</div>` : ''}
      ${h.reviewCount > 0 ? `<div class="card-review-meta">리뷰 ${h.reviewCount}개 · 점수 ${h.score > 0 ? '+' : ''}${h.score}${!h.reliable ? ' <span class="badge-low-trust">신뢰도 낮음</span>' : ''}</div>` : ''}
    `;
    card.onclick = () => openDetail(h);
    list.appendChild(card);
  });
}

function openDetail(hospital) {
  document.querySelectorAll('.hospital-card').forEach(c => c.classList.remove('selected'));
  const card = document.querySelector(`.hospital-card[data-id="${hospital.id}"]`);
  if (card) card.classList.add('selected');

  // 상세 페이지에서 사용할 병원 데이터를 sessionStorage에 저장
  sessionStorage.setItem('selectedHospital', JSON.stringify(hospital));

  if (kakaoMap) {
    kakaoMap.setCenter(new kakao.maps.LatLng(hospital.lat, hospital.lng));
  }

  window.location.href = `/hospitals/${encodeURIComponent(hospital.id)}`;
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
    loadHospitals();
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

window.onLocationSet = () => loadHospitals();

document.addEventListener('DOMContentLoaded', () => {
  if (KAKAO_JS_API_KEY && KAKAO_JS_API_KEY !== '') {
    initMap();
  } else {
    loadHospitals();
  }
});
