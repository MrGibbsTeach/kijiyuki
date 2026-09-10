const crypto = require('crypto');

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { answer } = req.body || {};
  if (!answer || typeof answer !== 'string') {
    return res.status(400).json({ error: 'Missing answer' });
  }

  const secret = process.env.AVAILABILITY_SECRET;
  const validAnswers = (process.env.AVAILABILITY_ANSWERS || '')
    .split(',')
    .map((a) => a.trim().toLowerCase())
    .filter(Boolean);

  if (!secret || validAnswers.length === 0) {
    return res.status(500).json({ error: 'Server not configured' });
  }

  const normalized = answer.trim().toLowerCase();
  if (!validAnswers.includes(normalized)) {
    // small delay to slow down brute-force guessing
    await new Promise((resolve) => setTimeout(resolve, 400));
    return res.status(401).json({ error: 'Incorrect answer' });
  }

  const exp = Date.now() + 1000 * 60 * 60 * 24 * 90; // 90 days
  const payload = Buffer.from(JSON.stringify({ exp })).toString('base64url');
  const signature = crypto.createHmac('sha256', secret).update(payload).digest('base64url');

  return res.status(200).json({ token: `${payload}.${signature}` });
};
