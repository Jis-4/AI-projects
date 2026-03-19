const state = {
  useCase: 'marketing',
  items: [],
  topRanked: [],
  promptData: null,
};

const form = document.getElementById('generate-form');
const gallery = document.getElementById('gallery');
const topRanked = document.getElementById('top-ranked');
const promptOutput = document.getElementById('prompt-output');
const statusText = document.getElementById('status-text');
const useCaseButtons = document.querySelectorAll('.use-case');
const template = document.getElementById('creative-card-template');

useCaseButtons.forEach((button) => {
  button.addEventListener('click', async () => {
    useCaseButtons.forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    state.useCase = button.dataset.useCase;
    document.getElementById('use_case').value = state.useCase;
    document.getElementById('stat-usecase').textContent = state.useCase;
    await refreshGallery();
  });
});

document.getElementById('refresh-gallery').addEventListener('click', refreshGallery);

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  statusText.textContent = 'Generating new creative directions...';
  const payload = Object.fromEntries(new FormData(form).entries());
  payload.variants = Number(payload.variants || 4);
  const response = await fetch('/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  state.promptData = data.prompt;
  state.items = data.created;
  state.topRanked = data.top_ranked;
  renderPrompt();
  renderTopRanked();
  await refreshGallery();
  statusText.textContent = 'Batch generated. Rate the outputs and edit the best concepts.';
});

function renderPrompt() {
  if (!state.promptData) {
    promptOutput.className = 'prompt-output empty';
    promptOutput.textContent = 'No optimized prompt yet.';
    return;
  }
  promptOutput.className = 'prompt-output';
  promptOutput.innerHTML = `
    <p><strong>Optimized prompt:</strong> ${state.promptData.optimized_prompt}</p>
    <p><strong>Negative prompt:</strong> ${state.promptData.negative_prompt}</p>
    <p><strong>Prompt score:</strong> ${state.promptData.prompt_score}</p>
    <ul>${state.promptData.recommendations.map((item) => `<li>${item}</li>`).join('')}</ul>
  `;
}

function renderTopRanked() {
  if (!state.topRanked.length) {
    topRanked.className = 'top-ranked empty';
    topRanked.textContent = 'No ranked creatives yet.';
    return;
  }
  topRanked.className = 'top-ranked';
  topRanked.innerHTML = state.topRanked.map((item) => `
    <div class="top-card">
      <strong>#${item.id} · ${item.headline}</strong>
      <span>Score: ${item.score}</span><br />
      <span>Rating: ${item.rating || 'not rated'} ${item.favorite ? '· favorite' : ''}</span><br />
      <span>${item.palette} / ${item.layout}</span>
    </div>
  `).join('');
  document.getElementById('stat-top').textContent = state.topRanked[0]?.score ?? 0;
}

async function refreshGallery() {
  const response = await fetch(`/api/images?use_case=${encodeURIComponent(state.useCase)}`);
  const data = await response.json();
  state.items = data.items;
  state.topRanked = data.top_ranked;
  renderGallery();
  renderTopRanked();
  document.getElementById('stat-images').textContent = state.items.length;
}

function renderGallery() {
  if (!state.items.length) {
    gallery.className = 'gallery empty';
    gallery.textContent = 'No images stored yet.';
    return;
  }
  gallery.className = 'gallery';
  gallery.textContent = '';
  state.items.forEach((item) => {
    const fragment = template.content.cloneNode(true);
    const card = fragment.querySelector('.creative-card');
    fragment.querySelector('.creative-preview').src = item.asset_path.replace(/^.*\/generated\//, '/generated/');
    fragment.querySelector('.creative-headline').textContent = item.headline;
    fragment.querySelector('.creative-meta').textContent = `${item.brand} · ${item.product} · ${item.palette} / ${item.layout}`;
    fragment.querySelector('.creative-score').textContent = `Score ${item.score} · ${item.rating ? `Rated ${item.rating}/5` : 'Unrated'}`;
    const favoriteButton = fragment.querySelector('.favorite-toggle');
    favoriteButton.textContent = item.favorite ? '★' : '☆';
    favoriteButton.addEventListener('click', () => submitRating(item.id, item.rating || 5, !item.favorite));

    const ratingGroup = fragment.querySelector('.rating-group');
    for (let value = 1; value <= 5; value += 1) {
      const button = document.createElement('button');
      button.textContent = `${value}★`;
      button.addEventListener('click', () => submitRating(item.id, value, item.favorite));
      ratingGroup.appendChild(button);
    }

    fragment.querySelector('.edit-submit').addEventListener('click', async () => {
      const editPayload = {
        mask_region: fragment.querySelector('.edit-mask-region').value,
        replacement_text: fragment.querySelector('.edit-replacement').value,
        edit_instruction: fragment.querySelector('.edit-instruction').value,
        palette: fragment.querySelector('.edit-palette').value,
        layout: fragment.querySelector('.edit-layout').value,
        style_strength: Number(fragment.querySelector('.edit-strength').value),
      };
      statusText.textContent = `Applying edit to creative #${item.id}...`;
      await fetch(`/api/images/${item.id}/edit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editPayload),
      });
      statusText.textContent = 'Edit applied. A new version was added to the gallery.';
      await refreshGallery();
    });

    gallery.appendChild(card);
  });
}

async function submitRating(id, rating, favorite) {
  await fetch(`/api/images/${id}/rate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rating, favorite }),
  });
  await refreshGallery();
}

refreshGallery();
