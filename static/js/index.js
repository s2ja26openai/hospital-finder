// static/js/index.js
const DEPARTMENTS = [
  '내과', '외과', '정형외과', '이비인후과', '피부과',
  '안과', '치과', '산부인과', '비뇨기과', '소아청소년과',
  '신경과', '정신건강의학과', '흉부외과', '성형외과', '재활의학과'
];

function renderDepts() {
  const grid = document.getElementById('deptGrid');
  DEPARTMENTS.forEach(dept => {
    const btn = document.createElement('button');
    btn.className = 'dept-btn';
    btn.textContent = dept;
    btn.onclick = () => goToHospitals(dept);
    grid.appendChild(btn);
  });
}

function goToChatbot() {
  const symptom = document.getElementById('symptomInput').value.trim();
  if (!symptom) {
    alert('증상을 입력해 주세요.');
    return;
  }
  const params = new URLSearchParams({ symptom });
  window.location.href = `/chatbot?${params}`;
}

function goToHospitals(dept) {
  const params = new URLSearchParams({ department: dept });
  window.location.href = `/hospitals?${params}`;
}

// Enter 키 지원
document.addEventListener('DOMContentLoaded', () => {
  renderDepts();
  const input = document.getElementById('symptomInput');
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') goToChatbot();
  });
});
