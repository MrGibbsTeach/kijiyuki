const crypto = require('crypto');

function verifyToken(token, secret) {
  if (!token || typeof token !== 'string') return false;
  const parts = token.split('.');
  if (parts.length !== 2) return false;
  const [payload, signature] = parts;

  const expectedSig = crypto.createHmac('sha256', secret).update(payload).digest('base64url');

  const sigBuf = Buffer.from(signature);
  const expectedBuf = Buffer.from(expectedSig);
  if (sigBuf.length !== expectedBuf.length) return false;
  if (!crypto.timingSafeEqual(sigBuf, expectedBuf)) return false;

  try {
    const data = JSON.parse(Buffer.from(payload, 'base64url').toString());
    return typeof data.exp === 'number' && Date.now() < data.exp;
  } catch {
    return false;
  }
}

module.exports = async function handler(req, res) {
  const secret = process.env.AVAILABILITY_SECRET;
  const calendarUrl = process.env.CALENDAR_EMBED_URL;

  if (!secret || !calendarUrl) {
    return res.status(500).json({ error: 'Server not configured' });
  }

  const authHeader = req.headers.authorization || '';
  const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : '';

  if (!verifyToken(token, secret)) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }

  return res.status(200).json({ url: calendarUrl });
};
