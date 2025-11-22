const API_BASE_URL = '/api';

let allPhotos = [];
let currentPhotos = [];
let currentPhotoIndex = 0;
let selectedFile = null;

// Elements
const selfieInput = document.getElementById('selfieInput');
const uploadArea = document.getElementById('uploadArea');
const previewArea = document.getElementById('previewArea');
const previewImage = document.getElementById('previewImage');
const searchBtn = document.getElementById('searchBtn');
const cancelBtn = document.getElementById('cancelBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const matchResults = document.getElementById('matchResults');
const galleryGrid = document.getElementById('galleryGrid');
const photoCount = document.getElementById('photoCount');
const showAllBtn = document.getElementById('showAllBtn');
const imageModal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const modalClose = document.querySelector('.modal-close');
const downloadBtn = document.getElementById('downloadBtn');
const modalPrev = document.getElementById('modalPrev');
const modalNext = document.getElementById('modalNext');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadAllPhotos();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    selfieInput.addEventListener('change', handleFileSelect);
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        if (e.dataTransfer.files.length > 0) {
            selectedFile = e.dataTransfer.files[0];
            showPreview();
        }
    });
    
    searchBtn.addEventListener('click', performFaceMatch);
    cancelBtn.addEventListener('click', resetUpload);
    showAllBtn.addEventListener('click', () => {
        matchResults.style.display = 'none';
        resetUpload();
        displayGallery(allPhotos);
        galleryGrid.scrollIntoView({ behavior: 'smooth' });
    });
    
    modalClose.addEventListener('click', closeModal);
    
    imageModal.addEventListener('click', (e) => {
        if (e.target === imageModal) {
            closeModal();
        }
    });

    downloadBtn.addEventListener('click', downloadCurrentImage);
    modalPrev.addEventListener('click', showPreviousImage);
    modalNext.addEventListener('click', showNextImage);

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (imageModal.style.display === 'block') {
            if (e.key === 'Escape') closeModal();
            else if (e.key === 'ArrowLeft') showPreviousImage();
            else if (e.key === 'ArrowRight') showNextImage();
        }
    });
}

function handleFileSelect(e) {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        showPreview();
    }
}

function showPreview() {
    if (!selectedFile) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        uploadArea.style.display = 'none';
        previewArea.style.display = 'flex';
    };
    reader.readAsDataURL(selectedFile);
}

function resetUpload() {
    selectedFile = null;
    selfieInput.value = '';
    uploadArea.style.display = 'block';
    previewArea.style.display = 'none';
    matchResults.style.display = 'none';
}

async function loadAllPhotos() {
    try {
        const response = await fetch(`${API_BASE_URL}/photos`);
        const data = await response.json();
        
        if (data.success) {
            allPhotos = data.photos;
            displayGallery(allPhotos);
            photoCount.textContent = `${allPhotos.length} photos`;
        } else {
            showError('Failed to load photos');
        }
    } catch (error) {
        console.error('Error loading photos:', error);
        showError('Failed to load photos. Make sure the server is running.');
    }
}

async function performFaceMatch() {
    if (!selectedFile) return;
    
    previewArea.style.display = 'none';
    loadingIndicator.style.display = 'block';
    matchResults.style.display = 'none';
    
    try {
        const formData = new FormData();
        formData.append('photo', selectedFile);
        
        const response = await fetch(`${API_BASE_URL}/face-match`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        loadingIndicator.style.display = 'none';
        
        if (data.success) {
            displayMatchResults(data.matchedPhotos, data.totalMatches);
        } else {
            showError(data.error || 'Face matching failed');
            previewArea.style.display = 'flex';
        }
    } catch (error) {
        console.error('Error in face matching:', error);
        loadingIndicator.style.display = 'none';
        showError('Face matching failed. Please try again.');
        previewArea.style.display = 'flex';
    }
}

function displayMatchResults(photos, totalMatches) {
    matchResults.style.display = 'block';
    
    if (totalMatches === 0) {
        matchResults.innerHTML = `
            <div class="no-matches">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="15" y1="9" x2="9" y2="15"/>
                    <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
                <h3>No matches found</h3>
                <p>We couldn't find any photos with your face. Try uploading a different photo or check the gallery below.</p>
                <button class="btn btn-primary" onclick="resetUpload()">Try Again</button>
            </div>
        `;
    } else {
        currentPhotos = photos;
        matchResults.innerHTML = `
            <h3>🎉 Found ${totalMatches} photo${totalMatches > 1 ? 's' : ''} with you!</h3>
            <div class="gallery-grid" id="matchGallery"></div>
            <div style="text-align: center; margin-top: 20px;">
                <button class="btn btn-secondary" onclick="resetUpload()">⬅ Back to Search</button>
            </div>
        `;
        
        const matchGallery = document.getElementById('matchGallery');
        photos.forEach((photo, index) => {
            const item = createGalleryItem(photo, index, photos);
            matchGallery.appendChild(item);
        });
        
        matchResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function displayGallery(photos) {
    galleryGrid.innerHTML = '';
    currentPhotos = photos;
    
    if (photos.length === 0) {
        galleryGrid.innerHTML = '<p style="text-align: center; padding: 40px; color: #666;">No photos available</p>';
        return;
    }
    
    photos.forEach((photo, index) => {
        const item = createGalleryItem(photo, index, photos);
        galleryGrid.appendChild(item);
    });
}

function createGalleryItem(photo, index, photoArray) {
    const item = document.createElement('div');
    item.className = 'gallery-item';
    item.style.animationDelay = `${index * 0.05}s`;
    
    const img = document.createElement('img');
    img.src = photo.url;
    img.alt = `Wedding photo ${index + 1}`;
    img.loading = 'lazy';
    
    // Download overlay
    const downloadOverlay = document.createElement('div');
    downloadOverlay.className = 'download-overlay';
    
    const downloadBtnSmall = document.createElement('button');
    downloadBtnSmall.className = 'download-btn-small';
    downloadBtnSmall.title = 'Download';
    downloadBtnSmall.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
    `;
    
    downloadBtnSmall.addEventListener('click', (e) => {
        e.stopPropagation();
        downloadImage(photo.fullUrl || photo.url, `wedding-photo-${index + 1}.jpg`);
    });
    
    downloadOverlay.appendChild(downloadBtnSmall);
    item.appendChild(img);
    item.appendChild(downloadOverlay);
    
    item.addEventListener('click', () => {
        openModal(index, photoArray);
    });
    
    return item;
}

function openModal(index, photoArray) {
    currentPhotoIndex = index;
    currentPhotos = photoArray;
    modalImage.src = photoArray[index].fullUrl || photoArray[index].url;
    imageModal.style.display = 'block';
    updateModalNavigation();
}

function closeModal() {
    imageModal.style.display = 'none';
}

function showPreviousImage() {
    if (currentPhotoIndex > 0) {
        currentPhotoIndex--;
        modalImage.src = currentPhotos[currentPhotoIndex].fullUrl || currentPhotos[currentPhotoIndex].url;
        updateModalNavigation();
    }
}

function showNextImage() {
    if (currentPhotoIndex < currentPhotos.length - 1) {
        currentPhotoIndex++;
        modalImage.src = currentPhotos[currentPhotoIndex].fullUrl || currentPhotos[currentPhotoIndex].url;
        updateModalNavigation();
    }
}

function updateModalNavigation() {
    modalPrev.style.display = currentPhotoIndex > 0 ? 'flex' : 'none';
    modalNext.style.display = currentPhotoIndex < currentPhotos.length - 1 ? 'flex' : 'none';
}

function downloadCurrentImage() {
    const currentPhoto = currentPhotos[currentPhotoIndex];
    downloadImage(currentPhoto.fullUrl || currentPhoto.url, `wedding-photo-${currentPhotoIndex + 1}.jpg`);
}

function downloadImage(url, filename) {
    fetch(url)
        .then(response => response.blob())
        .then(blob => {
            const blobUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = blobUrl;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(blobUrl);
        })
        .catch(error => {
            console.error('Download failed:', error);
            // Fallback: open in new tab
            window.open(url, '_blank');
        });
}

function showError(message) {
    alert(message);
}
