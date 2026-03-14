// static/js/location.js
// 위치 상태를 전역으로 관리 (다른 페이지 JS에서 사용)
window.LocationState = {
  lat: 37.5665,   // 기본값: 서울 시청 (Mock)
  lng: 126.9780,
  label: '현재 위치',
  isSet: false
};

function showLocationModal() {
  document.getElementById('locationModal').classList.remove('hidden');
  document.getElementById('addressInput').focus();
}

function hideLocationModal() {
  document.getElementById('locationModal').classList.add('hidden');
}

function requestGPS() {
  if (!navigator.geolocation) {
    showLocationModal();
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      window.LocationState.lat = pos.coords.latitude;
      window.LocationState.lng = pos.coords.longitude;
      window.LocationState.label = '현재 위치 (GPS)';
      window.LocationState.isSet = true;
      updateLocationBar();
      hideLocationModal();
      if (typeof onLocationSet === 'function') onLocationSet();
    },
    () => {
      // GPS 권한 거부 시 주소 입력 fallback
      showLocationModal();
    },
    { timeout: 8000 }
  );
}

async function confirmAddress() {
  const val = document.getElementById('addressInput').value.trim();
  if (!val) return;

  try {
    const res = await fetch('/api/geocode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ address: val }),
    });
    const data = await res.json();
    if (data.error || !data.lat) {
      alert('주소를 찾을 수 없습니다. 다시 입력해 주세요.');
      return;
    }
    window.LocationState.lat = data.lat;
    window.LocationState.lng = data.lng;
    window.LocationState.label = val;
    window.LocationState.isSet = true;
    updateLocationBar();
    hideLocationModal();
    if (typeof onLocationSet === 'function') onLocationSet();
  } catch (e) {
    alert('위치 설정 중 오류가 발생했습니다.');
  }
}

function updateLocationBar() {
  const el = document.getElementById('locationBarText');
  if (el) el.textContent = window.LocationState.label;
}

// 모달 HTML을 동적으로 삽입
function injectLocationModal() {
  const html = `
    <div id="locationModal" class="modal-overlay hidden">
      <div class="modal">
        <div class="modal-title">위치 설정</div>
        <div class="modal-desc">주소 또는 지명을 입력하거나 GPS로 현재 위치를 확인하세요.</div>
        <input id="addressInput" class="modal-input" type="text"
               placeholder="예: 서울 강남구 역삼동"
               onkeydown="if(event.key==='Enter') confirmAddress()">
        <div class="modal-actions">
          <button class="btn btn-outline" onclick="requestGPS()">GPS 사용</button>
          <button class="btn btn-primary" onclick="confirmAddress()">확인</button>
        </div>
      </div>
    </div>
  `;
  document.body.insertAdjacentHTML('beforeend', html);
}

document.addEventListener('DOMContentLoaded', () => {
  injectLocationModal();
  // 페이지 최초 로딩 시 GPS 자동 요청
  requestGPS();
});
