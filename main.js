document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('microbit-form');
  const status = document.getElementById('status');

  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    const action = document.getElementById('action').value;
    const option = document.getElementById('option').value;
    const channel = document.getElementById('channel').value;
    const mobile = document.getElementById('mobile').checked;

    const payload = { action, option, channel, mobile };

    status.innerText = 'Sending command...';

    try {
      const resp = await fetch('/microbit/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || 'Unknown error');
      status.innerText = 'Result: ' + JSON.stringify(data);
    } catch (err) {
      status.innerText = 'Error: ' + err.message;
    }
  });
});
