const express = require('express');
const path = require('path');
const fs = require('fs');
const archiver = require('archiver');

const app = express();
const PORT = 3000;

// Serve static files (images & index.html)
app.use(express.static(path.join(__dirname, 'public')));

// Serve index.html
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Route to download single image
app.get('/download/kittenz123', (req, res) => {
  const filePath = path.join(__dirname, 'public', 'images', 'kittenz123.jpg');
  res.download(filePath, 'kittenz123.jpg');
});

app.get('/download/cuteKitten', (req, res) => {
  const filePath = path.join(__dirname, 'public', 'images', 'cuteKitten.jpg');
  res.download(filePath, 'cuteKitten.jpg');
});

// Route to download directory as ZIP
app.get('/download/zip', (req, res) => {
  const dirPath = path.join(__dirname, 'public', 'images');
  res.setHeader('Content-Type', 'application/zip');
  res.setHeader('Content-Disposition', 'attachment; filename=images.zip');

  const archive = archiver('zip', { zlib: { level: 9 } });
  archive.directory(dirPath, false);
  archive.pipe(res);
  archive.finalize();
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
