document.addEventListener('DOMContentLoaded', () => {
    const claimForm = document.getElementById('claimForm');
    
    if (claimForm) {
        claimForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const name = document.getElementById('nameInput').value;
            const email = document.getElementById('emailInput').value;
            const college = document.getElementById('collegeInput').value;
            const msgArea = document.getElementById('messageArea');
            const btn = document.getElementById('claimBtn');
            
            if (!name && !email && !college) {
                msgArea.innerHTML = '<div class="alert alert-warning py-2 small"><i class="bi bi-exclamation-triangle me-2"></i>Please enter at least one field to search.</div>';
                return;
            }
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>PROCESSING...';
            msgArea.innerHTML = '';
            
            try {
                const response = await fetch('/api/claim', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name, email, college })
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    showSuccess(result.data);
                } else if (result.status === 'already_claimed') {
                    showWarning(result.message);
                } else if (result.status === 'not_found') {
                    showError(result.message);
                } else {
                    showError(result.message || 'An unknown error occurred.');
                }
            } catch (error) {
                showError('Network error. Please try again.');
            } finally {
                btn.disabled = false;
                btn.innerHTML = 'CLAIM FOOD TOKEN <i class="bi bi-arrow-right ms-2"></i>';
            }
        });
    }
});

function showSuccess(data) {
    document.getElementById('claimFormContainer').classList.add('d-none');
    
    const resultContainer = document.getElementById('resultContainer');
    resultContainer.classList.remove('d-none');
    resultContainer.classList.add('animate-fade-in');
    
    document.getElementById('resultIcon').style.background = 'var(--success)';
    document.getElementById('resultIcon').innerHTML = '<i class="bi bi-check-lg"></i>';
    document.getElementById('resultTitle').textContent = 'FOOD TOKEN CLAIMED';
    document.getElementById('resultSubtitle').textContent = 'Please show this screen at the food counter.';
    
    document.getElementById('tokenDetails').classList.remove('d-none');
    document.getElementById('resName').textContent = data.name;
    document.getElementById('resCollege').textContent = data.college;
    document.getElementById('resTokenId').textContent = data.token_id;
}

function showWarning(message) {
    document.getElementById('claimFormContainer').classList.add('d-none');
    
    const resultContainer = document.getElementById('resultContainer');
    resultContainer.classList.remove('d-none');
    resultContainer.classList.add('animate-fade-in');
    
    document.getElementById('resultIcon').style.background = 'var(--warning)';
    document.getElementById('resultIcon').innerHTML = '<i class="bi bi-exclamation-triangle"></i>';
    document.getElementById('resultTitle').textContent = 'ALREADY CLAIMED';
    document.getElementById('resultSubtitle').textContent = message;
    
    document.getElementById('tokenDetails').classList.add('d-none');
}

function showError(message) {
    document.getElementById('claimFormContainer').classList.add('d-none');
    
    const resultContainer = document.getElementById('resultContainer');
    resultContainer.classList.remove('d-none');
    resultContainer.classList.add('animate-fade-in');
    
    document.getElementById('resultIcon').style.background = 'var(--danger)';
    document.getElementById('resultIcon').innerHTML = '<i class="bi bi-x-lg"></i>';
    document.getElementById('resultTitle').textContent = 'NOT FOUND';
    document.getElementById('resultSubtitle').textContent = message;
    
    document.getElementById('tokenDetails').classList.add('d-none');
}

function resetForm() {
    document.getElementById('resultContainer').classList.add('d-none');
    
    const claimFormContainer = document.getElementById('claimFormContainer');
    claimFormContainer.classList.remove('d-none');
    claimFormContainer.classList.add('animate-fade-in');
    
    document.getElementById('claimForm').reset();
    document.getElementById('messageArea').innerHTML = '';
}
