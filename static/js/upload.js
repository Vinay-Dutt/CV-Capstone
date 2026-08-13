/**
 * Drag & Drop Image Upload & AJAX Analysis Submission Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    initDropzone();
    initUploadForm();
});

let selectedFiles = [];

function initDropzone() {
    const dropzone = document.getElementById('imageDropzone');
    const fileInput = document.getElementById('fileInput');
    const previewContainer = document.getElementById('previewContainer');
    
    if (!dropzone || !fileInput) return;
    
    dropzone.addEventListener('click', () => fileInput.click());
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('drag-over');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('drag-over');
        });
    });
    
    dropzone.addEventListener('drop', (e) => {
        const files = Array.from(e.dataTransfer.files);
        handleFilesSelected(files);
    });
    
    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFilesSelected(files);
    });
}

function handleFilesSelected(files) {
    const validExtensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif'];
    const maxMB = 32;
    
    const validFiles = files.filter(file => {
        const ext = file.name.split('.').pop().toLowerCase();
        const sizeMB = file.size / (1024 * 1024);
        
        if (!validExtensions.includes(ext)) {
            showToast(`File "${file.name}" has an unsupported format.`, 'danger');
            return false;
        }
        if (sizeMB > maxMB) {
            showToast(`File "${file.name}" exceeds the max limit of 32MB.`, 'danger');
            return false;
        }
        return true;
    });
    
    // Append newly selected files while filtering out duplicates
    const newFiles = validFiles.filter(vf => !selectedFiles.some(sf => sf.name === vf.name && sf.size === vf.size));
    selectedFiles = [...selectedFiles, ...newFiles];
    renderFilePreviews(selectedFiles);
}

function renderFilePreviews(files) {
    const previewContainer = document.getElementById('previewContainer');
    const fileCountBadge = document.getElementById('selectedFileCount');
    const submitBtn = document.getElementById('startAnalysisBtn');
    
    if (!previewContainer) return;
    
    previewContainer.innerHTML = '';
    if (fileCountBadge) fileCountBadge.textContent = `${files.length} File(s) Selected`;
    if (submitBtn) submitBtn.disabled = files.length === 0;
    
    files.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const col = document.createElement('div');
            col.className = 'col-6 col-md-4 col-lg-3 animate-fade-in';
            col.innerHTML = `
                <div class="glass-card p-2 text-center position-relative">
                    <div class="image-preview-wrapper mb-2">
                        <img src="${e.target.result}" alt="${file.name}">
                    </div>
                    <p class="small text-truncate mb-0 font-monospace">${file.name}</p>
                    <span class="badge bg-secondary small">${(file.size/1024).toFixed(1)} KB</span>
                    <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 m-1 rounded-circle" onclick="removeSelectedFile(${index})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            previewContainer.appendChild(col);
        };
        reader.readAsDataURL(file);
    });
}

function removeSelectedFile(index) {
    selectedFiles.splice(index, 1);
    renderFilePreviews(selectedFiles);
}
window.removeSelectedFile = removeSelectedFile;

function initUploadForm() {
    const form = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('startAnalysisBtn');
    const progressBar = document.getElementById('uploadProgressBar');
    const progressContainer = document.getElementById('progressContainer');
    
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (selectedFiles.length === 0) {
            showToast('Please select at least one valid image to proceed.', 'warning');
            return;
        }
        
        const isBatch = selectedFiles.length > 1;
        const endpoint = isBatch ? '/api/compare' : '/api/analyze';
        
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append(isBatch ? 'images' : 'image', file);
        });
        
        // Optional Preprocessing Parameter Toggles
        const gaussianKernel = document.getElementById('gaussianKernelSelect')?.value || 5;
        const cannyLow = document.getElementById('cannyLowInput')?.value || 50;
        const cannyHigh = document.getElementById('cannyHighInput')?.value || 150;
        
        formData.append('gaussian_kernel', gaussianKernel);
        formData.append('canny_low', cannyLow);
        formData.append('canny_high', cannyHigh);
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Analyzing Vision Features...';
        if (progressContainer) progressContainer.classList.remove('d-none');
        if (progressBar) progressBar.style.width = '30%';
        
        try {
            if (progressBar) progressBar.style.width = '65%';
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });
            
            if (progressBar) progressBar.style.width = '95%';
            const data = await response.json();
            
            if (response.ok && data.success) {
                if (progressBar) progressBar.style.width = '100%';
                showToast('Image Complexity Index analysis completed successfully!', 'success');
                
                setTimeout(() => {
                    if (isBatch) {
                        window.location.href = `/comparison?id=${data.comparison_id}`;
                    } else {
                        window.location.href = `/dashboard?id=${data.analysis_id}`;
                    }
                }, 500);
            } else {
                throw new Error(data.error || 'Server error during feature calculation.');
            }
        } catch (err) {
            showToast(err.message, 'danger');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-microscope me-2"></i> Run Complexity Assessment';
            if (progressContainer) progressContainer.classList.add('d-none');
        }
    });
}
