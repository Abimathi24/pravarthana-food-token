document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    
    // Setup file upload
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('fileInput');
            const statusDiv = document.getElementById('uploadStatus');
            const btn = document.getElementById('uploadBtn');
            
            if (!fileInput.files.length) {
                statusDiv.innerHTML = '<span class="text-danger">Please select a file</span>';
                return;
            }
            
            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Uploading...';
            statusDiv.innerHTML = '';
            
            try {
                const response = await fetch('/admin/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    statusDiv.innerHTML = `<span class="text-success"><i class="bi bi-check-circle me-1"></i>${result.success}</span>`;
                    loadStats(); // Refresh dashboard
                    fileInput.value = ''; // Reset
                } else {
                    statusDiv.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-triangle me-1"></i>${result.error}</span>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-triangle me-1"></i>Upload failed. Ensure server is running.</span>`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-cloud-upload me-2"></i>Upload Data';
            }
        });
    }
    
    // Setup add participant
    const addForm = document.getElementById('addParticipantForm');
    if (addForm) {
        addForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('addName').value;
            const email = document.getElementById('addEmail').value;
            const college = document.getElementById('addCollege').value;
            const statusDiv = document.getElementById('addStatus');
            const btn = document.getElementById('addBtn');
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Adding...';
            statusDiv.innerHTML = '';
            
            try {
                const response = await fetch('/admin/api/add_participant', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name, email, college })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    statusDiv.innerHTML = `<span class="text-success"><i class="bi bi-check-circle me-1"></i>${result.success}</span>`;
                    loadStats(); // Refresh dashboard stats
                    addForm.reset();
                } else {
                    statusDiv.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-triangle me-1"></i>${result.error}</span>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-triangle me-1"></i>Failed to add participant.</span>`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-plus-circle me-1"></i> Add Participant';
            }
        });
    }
});

async function loadStats() {
    try {
        const response = await fetch('/admin/api/stats');
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('stat-total').textContent = data.total;
            document.getElementById('stat-claimed').textContent = data.claimed;
            document.getElementById('stat-not-claimed').textContent = data.not_claimed;
            
            const tbody = document.getElementById('claimsTableBody');
            tbody.innerHTML = '';
            
            if (data.recent_claims && data.recent_claims.length > 0) {
                data.recent_claims.forEach(claim => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>
                            <div class="fw-bold">${claim.name}</div>
                            <div class="small text-muted">${claim.email}</div>
                        </td>
                        <td>${claim.college}</td>
                        <td class="font-monospace text-primary">${claim.token_id || '-'}</td>
                        <td class="small">${claim.claim_time || '-'}</td>
                        <td><span class="badge badge-claimed">CLAIMED</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteParticipant('${claim.id}')" title="Delete Participant">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4">No tokens claimed yet.</td></tr>';
            }
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

async function deleteParticipant(participantId) {
    if (!confirm('Are you sure you want to delete this participant?')) {
        return;
    }
    
    try {
        const response = await fetch(`/admin/api/delete_participant/${participantId}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        
        if (response.ok) {
            loadStats(); // Refresh table
        } else {
            alert('Failed to delete: ' + result.error);
        }
    } catch (error) {
        alert('An error occurred while deleting the participant.');
    }
}

async function wipeDatabase() {
    const btn = document.getElementById('confirmWipeBtn');
    const statusDiv = document.getElementById('wipeStatus');
    
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Wiping...';
    statusDiv.innerHTML = '';
    
    try {
        const response = await fetch('/admin/api/wipe_database', {
            method: 'DELETE'
        });
        const result = await response.json();
        
        if (response.ok) {
            statusDiv.innerHTML = `<span class="text-success"><i class="bi bi-check-circle me-1"></i>${result.success}</span>`;
            loadStats(); // Refresh table
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('wipeModal'));
                if (modal) modal.hide();
                statusDiv.innerHTML = ''; // reset
            }, 2000);
        } else {
            statusDiv.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-triangle me-1"></i>${result.error}</span>`;
        }
    } catch (error) {
        statusDiv.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-triangle me-1"></i>Failed to wipe database.</span>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Yes, Wipe Database';
    }
}
