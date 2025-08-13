const Sentiment = require('sentiment');
const sentiment = new Sentiment();
const XLSX = require('xlsx');
const fs = require('fs');

// Read uploaded file
const workbook = XLSX.readFile('uploads/user_uploaded.xlsx');
const sheet = workbook.Sheets[workbook.SheetNames[0]];
const data = XLSX.utils.sheet_to_json(sheet);

// Enrich
const enriched = data.map(post => {
  const result = sentiment.analyze(post.text);
  let label = 'neutral';
  let severity = 'low';
  const score = result.score;

  if (score > 1) label = 'positive';
  else if (score < -1) label = 'negative';

  if (Math.abs(score) > 3) severity = 'high';
  else if (Math.abs(score) > 1) severity = 'medium';

  // Dummy topic detection (can improve later)
  let topic = '';
  const lower = post.text.toLowerCase();
  if (lower.includes('claim')) topic = 'claims';
  else if (lower.includes('price')) topic = 'pricing';
  else if (lower.includes('service')) topic = 'service';
  else if (lower.includes('onboard')) topic = 'onboarding';

  return {
    ...post,
    score,
    sentiment: label,
    severity,
    topic
  };
});

const newSheet = XLSX.utils.json_to_sheet(enriched);
const newBook = XLSX.utils.book_new();
XLSX.utils.book_append_sheet(newBook, newSheet, 'EnrichedPosts');

XLSX.writeFile(newBook, 'processed/sbi_enriched_sentiment_data.xlsx');

console.log("✅ Enrichment complete.");
