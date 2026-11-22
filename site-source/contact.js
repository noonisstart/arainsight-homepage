const form = document.querySelector('#inquiry');
const endpoint = form.dataset.endpoint;
const status = form.querySelector('.submission-status');
const button = form.querySelector('button');
let pending = false;
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!endpoint || pending || !form.reportValidity()) return;
  pending = true;
  button.disabled = true;
  status.textContent = '상담 신청을 보내는 중입니다.';
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      body: new FormData(form),
      headers: { Accept: 'application/json' }
    });
    if (!response.ok) throw new Error('Submission rejected');
    form.reset();
    status.textContent = '상담 신청이 접수되었습니다.';
  } catch {
    status.textContent = '접수 여부를 확인하지 못했습니다. 네트워크 상태를 확인해 주세요.';
  } finally {
    pending = false;
    button.disabled = false;
  }
});
