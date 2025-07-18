// © 2024–2025 Harnisch LLC. All Rights Reserved.
// Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
// Unauthorized use, distribution, or modification is prohibited.

// Store user answers
const answers = {};
const situation = [];
const states = []; // Array for multiple state selections
const interests = []; // Array for multiple interests
let currentQuestion = 1;
const totalQuestions = 5; // Age, Gender, State, Situation, Interests
// Load ministries from server (protected)
let ministries = {};
let loadingRetries = 0;
const maxRetries = 3;

// Progress messages for each step
const progressMessages = {
    1: "Let's get started!",
    2: "Great! Keep going...",
    3: "You're doing great!",
    4: "Almost there!",
    5: "Last question!"
};

async function loadMinistries() {
    try {
        console.log('PWA: Starting to load ministries...');
        
        const response = await fetch('/api/get-ministries', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            },
            timeout: 10000 // 10 second timeout
        });
        
        console.log('PWA: API response status:', response.status);
        
        if (response.ok) {
            ministries = await response.json();
            console.log('PWA: Ministries loaded successfully, count:', Object.keys(ministries).length);
            
            // Hide loading screen on success
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) {
                console.log('PWA: Hiding loading overlay');
                overlay.style.opacity = '0';
                setTimeout(() => {
                    overlay.style.display = 'none';
                }, 500);
            }
        } else {
            throw new Error(`Server error: ${response.status}`);
        }
    } catch (error) {
        console.error('PWA: Error loading ministries:', error);
        loadingRetries++;
        
        if (loadingRetries < maxRetries) {
            // Retry after a delay
            const retryDelay = loadingRetries * 2000; // 2s, 4s, 6s
            console.log(`PWA: Retrying in ${retryDelay}ms (attempt ${loadingRetries + 1}/${maxRetries})`);
            
            // Update loading message
            const loadingText = document.querySelector('.loading-text');
            const loadingSubtext = document.querySelector('.loading-subtext');
            if (loadingText) {
                loadingText.textContent = 'Still loading...';
            }
            if (loadingSubtext) {
                loadingSubtext.textContent = `Attempt ${loadingRetries + 1} of ${maxRetries}. Please wait...`;
            }
            
            setTimeout(() => loadMinistries(), retryDelay);
        } else {
            // Show error message after all retries failed
            console.error('PWA: All retries failed, showing error');
            showLoadingError();
        }
    }
}

// Add a global fallback to ensure loading overlay doesn't get stuck
setTimeout(() => {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay && overlay.style.display !== 'none') {
        console.log('PWA: Global fallback - forcing overlay hide after 20 seconds');
        overlay.style.opacity = '0';
        setTimeout(() => {
            overlay.style.display = 'none';
        }, 500);
    }
}, 20000); // 20 second global fallback

function showLoadingError() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 48px; margin-bottom: 20px;">😔</div>
                <div class="loading-text" style="color: #dc3545; font-size: 24px; margin-bottom: 10px;">
                    Unable to Load Ministry Finder
                </div>
                <div class="loading-subtext" style="color: #666; margin-bottom: 20px;">
                    We're having trouble connecting to our server. This could be temporary.
                </div>
                <div style="margin-bottom: 20px;">
                    <button id="retryButton" style="padding: 10px 20px; background: #005921; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px;">
                        🔄 Try Again
                    </button>
                </div>
                <div style="color: #666; font-size: 14px;">
                    If this problem continues, please contact:<br>
                    📧 <a href="mailto:support@stedward.org" style="color: #005921;">support@stedward.org</a><br>
                    📞 (615) 833-5520
                </div>
            </div>
        `;
        
        // Add event listener to retry button
        document.getElementById('retryButton').addEventListener('click', function() {
            location.reload();
        });
    }
}

// ENHANCED Age-specific interest options with improved emojis
const interestOptions = {
    infant: [
        { value: 'support', label: '👥 Parent Support & Community' },
        { value: 'education', label: '📖 Learning About Faith' },
        { value: 'service', label: '🤝 Helping Others' },
        { value: 'all', label: '✨ Show me everything!' }
    ],
    elementary: [
        { value: 'education', label: '📚 Learning & Growing in Faith' },
        { value: 'fellowship', label: '🎯 Making Friends' },
        { value: 'music', label: '🎵 Music & Arts' },
        { value: 'service', label: '🤝 Helping Others' },
        { value: 'all', label: '✨ Show me everything!' }
    ],
    'junior-high': [
        { value: 'fellowship', label: '👥 Fellowship & Community' },
        { value: 'education', label: '📖 Learning & Teaching' },
        { value: 'service', label: '🙏 Serving Others' },
        { value: 'prayer', label: '✝️ Prayer & Worship' },
        { value: 'all', label: '✨ Show me everything!' }
    ],
    'high-school': [
        { value: 'fellowship', label: '👥 Fellowship & Community' },
        { value: 'service', label: '🙏 Serving Others' },
        { value: 'prayer', label: '✝️ Prayer & Worship' },
        { value: 'music', label: '🎵 Music & Arts' },
        { value: 'education', label: '📖 Learning & Teaching' },
        { value: 'all', label: '✨ Show me everything!' }
    ],
    'college-young-adult': [
        { value: 'fellowship', label: '👥 Fellowship & Community' },
        { value: 'service', label: '🙏 Serving Others' },
        { value: 'prayer', label: '✝️ Prayer & Worship' },
        { value: 'education', label: '📖 Learning & Teaching' },
        { value: 'music', label: '🎵 Music & Arts' },
        { value: 'all', label: '✨ Show me everything!' }
    ],
    'married-parents': [
        { value: 'fellowship', label: '👥 Fellowship & Community' },
        { value: 'service', label: '🙏 Serving Others' },
        { value: 'education', label: '📖 Learning & Teaching' },
        { value: 'prayer', label: '✝️ Prayer & Worship' },
        { value: 'support', label: '👨‍👩‍👧‍👦 Family Support' },
        { value: 'kids', label: '👶 Something for my children' },
        { value: 'all', label: '✨ Show me everything!' }
    ],
    'journeying-adults': [
        { value: 'prayer', label: '✝️ Prayer & Worship' },
        { value: 'service', label: '🙏 Serving Others' },
        { value: 'fellowship', label: '👥 Fellowship & Community' },
        { value: 'education', label: '📖 Learning & Teaching' },
        { value: 'music', label: '🎵 Music & Arts' },
        { value: 'kids', label: '👶 Something for my children' },
        { value: 'all', label: '✨ Show me everything!' }
    ]
};

function answerQuestion(type, answer) {
    console.log('PWA: Answering question', currentQuestion, 'type:', type, 'answer:', answer);
    answers[type] = answer;
    
    // Update button styling
    const buttons = document.querySelectorAll(`#q${currentQuestion} .option-btn`);
    buttons.forEach(btn => btn.classList.remove('selected'));
    event.target.classList.add('selected');
    
    // Wait a moment for visual feedback
    setTimeout(() => {
        // For younger age groups, auto-assign single state but still show gender question
        if (type === 'age' && ['infant', 'elementary', 'junior-high', 'high-school'].includes(answer)) {
            states.push('single'); // Auto-assign single for younger ages
        }
        
        currentQuestion++;
        console.log('PWA: Moving to question', currentQuestion);
        
        // Skip question 3 (state in life) for younger age groups - UPDATED FOR ELEMENTARY
        if (currentQuestion === 3 && answers.age && ['infant', 'elementary', 'junior-high', 'high-school'].includes(answers.age)) {
            currentQuestion = 4; // Jump to situation question
            console.log('PWA: Skipping state question, jumping to question', currentQuestion);
        }
        
        // For interest question, populate age-specific options
        if (currentQuestion === 5) {
            populateInterestOptions();
        }
        
        updateProgress();
        showQuestion(currentQuestion);
    }, 300);
}

// State checkbox handling
function toggleStateCheckbox(value) {
    const checkbox = document.getElementById(`state-${value}`);
    checkbox.checked = !checkbox.checked;
    
    // Trigger the change handler
    handleStateCheckboxChange(value);
}

function handleStateCheckboxChange(value) {
    const checkbox = document.getElementById(`state-${value}`);
    const item = checkbox.parentElement;
    
    // Handle "none of above" logic
    if (value === 'none-of-above') {
        if (checkbox.checked) {
            // Clear all other checkboxes
            document.querySelectorAll('#state-checkboxes input[type="checkbox"]').forEach(cb => {
                if (cb.value !== 'none-of-above') {
                    cb.checked = false;
                    cb.parentElement.classList.remove('selected');
                }
            });
            states.length = 0; // Clear array
            states.push('none-of-above');
        }
    } else {
        // If selecting something else, uncheck "none of above"
        const noneCheckbox = document.getElementById('state-none-of-above');
        if (noneCheckbox && noneCheckbox.checked) {
            noneCheckbox.checked = false;
            noneCheckbox.parentElement.classList.remove('selected');
            const noneIndex = states.indexOf('none-of-above');
            if (noneIndex > -1) states.splice(noneIndex, 1);
        }
        
        // MUTUAL EXCLUSIVITY: Can't be both single AND married
        if (value === 'single' && checkbox.checked) {
            const marriedCheckbox = document.getElementById('state-married');
            if (marriedCheckbox && marriedCheckbox.checked) {
                marriedCheckbox.checked = false;
                marriedCheckbox.parentElement.classList.remove('selected');
                const marriedIndex = states.indexOf('married');
                if (marriedIndex > -1) states.splice(marriedIndex, 1);
            }
        } else if (value === 'married' && checkbox.checked) {
            const singleCheckbox = document.getElementById('state-single');
            if (singleCheckbox && singleCheckbox.checked) {
                singleCheckbox.checked = false;
                singleCheckbox.parentElement.classList.remove('selected');
                const singleIndex = states.indexOf('single');
                if (singleIndex > -1) states.splice(singleIndex, 1);
            }
        }
    }
    
    // Update the states array and styling
    if (checkbox.checked) {
        item.classList.add('selected');
        if (!states.includes(value)) {
            states.push(value);
        }
    } else {
        item.classList.remove('selected');
        const index = states.indexOf(value);
        if (index > -1) {
            states.splice(index, 1);
        }
    }
}

function nextFromState() {
    currentQuestion++;
    updateProgress();
    showQuestion(currentQuestion);
}

// Continue from Situation question to Interest question
function nextFromSituation() {
    currentQuestion++;
    // Before showing interest checkboxes, populate age-specific options
    populateInterestOptions();
    updateProgress();
    showQuestion(currentQuestion);
}

// Situation checkbox handling
function toggleSituationCheckbox(value) {
    const checkbox = document.getElementById(value);
    checkbox.checked = !checkbox.checked;
    
    // Trigger the change handler
    handleSituationCheckboxChange(value);
}

function handleSituationCheckboxChange(value) {
    const checkbox = document.getElementById(value);
    const item = checkbox.parentElement;
    
    // Handle "none of above" logic
    if (value === 'situation-none-of-above') {
        if (checkbox.checked) {
            // Clear all other checkboxes
            document.querySelectorAll('#situation-checkboxes input[type="checkbox"]').forEach(cb => {
                if (cb.id !== 'situation-none-of-above') {
                    cb.checked = false;
                    cb.parentElement.classList.remove('selected');
                }
            });
            situation.length = 0; // Clear array
            situation.push('situation-none-of-above');
        }
    } else {
        // If selecting something else, uncheck "none of above"
        const noneCheckbox = document.getElementById('situation-none-of-above');
        if (noneCheckbox && noneCheckbox.checked) {
            noneCheckbox.checked = false;
            noneCheckbox.parentElement.classList.remove('selected');
            const noneIndex = situation.indexOf('situation-none-of-above');
            if (noneIndex > -1) situation.splice(noneIndex, 1);
        }
    }
    
    // Update the situation array and styling
    if (checkbox.checked) {
        item.classList.add('selected');
        if (!situation.includes(value)) {
            situation.push(value);
        }
    } else {
        item.classList.remove('selected');
        const index = situation.indexOf(value);
        if (index > -1) {
            situation.splice(index, 1);
        }
    }
}

function populateInterestOptions() {
    const interestContainer = document.getElementById('interest-checkboxes');
    const ageGroup = answers.age;
    const options = interestOptions[ageGroup] || interestOptions['journeying-adults'];
    
    interestContainer.innerHTML = '';
    options.forEach(option => {
        const checkboxDiv = document.createElement('div');
        checkboxDiv.className = 'checkbox-item checkbox-clickable';
        checkboxDiv.dataset.value = option.value;
        
        checkboxDiv.innerHTML = `
            <input type="checkbox" id="interest-${option.value}" value="${option.value}">
            <label for="interest-${option.value}">
                <span class="checkbox-emoji">${option.label.split(' ')[0]}</span> ${option.label.substring(option.label.indexOf(' ') + 1)}
            </label>
        `;
        
        interestContainer.appendChild(checkboxDiv);
    });
    
    // Add event handlers to newly created interest checkboxes
    interestContainer.querySelectorAll('.checkbox-clickable').forEach(item => {
        item.addEventListener('click', function(e) {
            if (e.target.type !== 'checkbox' && e.target.tagName !== 'LABEL') {
                toggleInterestCheckbox(this.dataset.value);
            }
        });
    });
    
    interestContainer.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        cb.addEventListener('change', function() {
            handleInterestCheckboxChange(this.value);
        });
    });
}

function toggleInterestCheckbox(value) {
    const checkbox = document.getElementById(`interest-${value}`);
    checkbox.checked = !checkbox.checked;
    
    // Trigger the change handler
    handleInterestCheckboxChange(value);
}

function handleInterestCheckboxChange(value) {
    const checkbox = document.getElementById(`interest-${value}`);
    const item = checkbox.parentElement;
    
    // Handle "show me everything" logic
    if (value === 'all') {
        if (checkbox.checked) {
            // Clear all other checkboxes and select only "all"
            document.querySelectorAll('#interest-checkboxes input[type="checkbox"]').forEach(cb => {
                if (cb.value !== 'all') {
                    cb.checked = false;
                    cb.parentElement.classList.remove('selected');
                }
            });
            interests.length = 0; // Clear array
            interests.push('all');
        }
    } else {
        // If selecting something else, uncheck "show me everything"
        const allCheckbox = document.getElementById('interest-all');
        if (allCheckbox && allCheckbox.checked) {
            allCheckbox.checked = false;
            allCheckbox.parentElement.classList.remove('selected');
            const allIndex = interests.indexOf('all');
            if (allIndex > -1) interests.splice(allIndex, 1);
        }
    }
    
    // Update the interests array and styling
    if (checkbox.checked) {
        item.classList.add('selected');
        if (!interests.includes(value)) {
            interests.push(value);
        }
    } else {
        item.classList.remove('selected');
        const index = interests.indexOf(value);
        if (index > -1) {
            interests.splice(index, 1);
        }
    }
}

function goBack(questionNum) {
    // Clear selected styling
    document.querySelectorAll('.option-btn').forEach(btn => btn.classList.remove('selected'));
    document.querySelectorAll('.checkbox-item').forEach(item => item.classList.remove('selected'));
    
    // Clear checkbox states
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
    
    // Clear arrays when going back
    if (questionNum === 5) {
        interests.length = 0;
    }
    if (questionNum === 4) {
        situation.length = 0;
    }
    if (questionNum === 3) {
        states.length = 0;
    }
    
    // Handle going back when state question was skipped - UPDATED FOR ELEMENTARY
    if (questionNum === 4 && answers.age && ['infant', 'elementary', 'junior-high', 'high-school'].includes(answers.age)) {
        currentQuestion = 2; // Go back to gender question
    } else if (questionNum === 5 && answers.age && ['infant', 'elementary', 'junior-high', 'high-school'].includes(answers.age)) {
        currentQuestion = 4; // Go back to situation question
    } else {
        currentQuestion = questionNum - 1;
    }
    
    updateProgress();
    showQuestion(currentQuestion);
}

function showQuestion(questionNum) {
    console.log('PWA: Showing question', questionNum);
    document.querySelectorAll('.question').forEach(q => q.classList.remove('active'));
    const targetQuestion = document.getElementById(`q${questionNum}`);
    if (targetQuestion) {
        targetQuestion.classList.add('active');
        console.log('PWA: Question', questionNum, 'is now active');
    } else {
        console.error('PWA: Question', questionNum, 'not found in DOM');
    }
}

function updateProgress() {
    let totalQuestionsForUser = totalQuestions;
    // If younger age group, they skip state question, so only 4 questions total - UPDATED FOR ELEMENTARY
    if (answers.age && ['infant', 'elementary', 'junior-high', 'high-school'].includes(answers.age)) {
        totalQuestionsForUser = 4;
    }
    
    let progressQuestions = currentQuestion - 1;
    // Adjust for skipped question - UPDATED FOR ELEMENTARY
    if (currentQuestion >= 4 && answers.age && ['infant', 'elementary', 'junior-high', 'high-school'].includes(answers.age)) {
        progressQuestions = currentQuestion - 2; // Account for skipped state question
    }
    
    const progress = Math.min(progressQuestions / totalQuestionsForUser * 100, 100);
    const progressBar = document.getElementById('progress-bar');
    if (progressBar) {
        progressBar.style.width = progress + '%';
    }
    
    // Update progress text
    const progressText = document.getElementById('progress-text');
    if (progressText) {
        progressText.textContent = progressMessages[currentQuestion] || '';
    }
}

// NEW FUNCTION - Create selections summary
function createSelectionsummary() {
    const summaryItems = [];
    
    // Age group - UPDATED FOR ELEMENTARY
    if (answers.age) {
        const ageLabels = {
            'infant': 'Infant (0-3)',
            'elementary': 'Elementary School (PreK-Grade 5)', // CHANGED FROM 'kid'
            'junior-high': 'Junior High (Grades 6-8)',
            'high-school': 'High School (Grades 9-12)',
            'college-young-adult': 'College & Young Adult (18-35)',
            'married-parents': 'Married Couples & Parents',
            'journeying-adults': 'Journeying Adults (30+)'
        };
        summaryItems.push(`<strong>Age:</strong> ${ageLabels[answers.age]}`);
    }
    
    // Gender
    if (answers.gender && answers.gender !== 'skip') {
        summaryItems.push(`<strong>Gender:</strong> ${answers.gender.charAt(0).toUpperCase() + answers.gender.slice(1)}`);
    }
    
    // States (multi-select)
    if (states.length > 0 && !states.includes('none-of-above')) {
        const stateLabels = {
            'single': 'Single',
            'married': 'Married', 
            'parent': 'Parent'
        };
        const stateTexts = states.map(s => stateLabels[s] || s).join(', ');
        summaryItems.push(`<strong>State in Life:</strong> ${stateTexts}`);
    }
    
    // Situation (multi-select)
    if (situation.length > 0 && !situation.includes('situation-none-of-above')) {
        const situationLabels = {
            'new-to-stedward': 'New to St. Edward',
            'returning-to-church': 'Returning to Church',
            'new-to-nashville': 'New to Nashville',
            'current-parishioner': 'Current Parishioner',
            'just-curious': 'Just Exploring'
        };
        const situationTexts = situation.map(s => situationLabels[s] || s).join(', ');
        summaryItems.push(`<strong>Situation:</strong> ${situationTexts}`);
    }
    
    // Interests (multi-select)
    if (interests.length > 0) {
        const interestLabels = {
            'fellowship': 'Fellowship & Community',
            'service': 'Serving Others',
            'prayer': 'Prayer & Worship',
            'education': 'Learning & Teaching',
            'music': 'Music & Arts',
            'support': 'Family Support',
            'kids': 'Something for my children',
            'all': 'Show me everything!'
        };
        const interestTexts = interests.map(i => interestLabels[i] || i).join(', ');
        summaryItems.push(`<strong>Interests:</strong> ${interestTexts}`);
    }
    
    if (summaryItems.length === 0) {
        return '';
    }
    
    return `
        <div class="selections-summary">
            <h3>🎯 Your Path Profile:</h3>
            <p>${summaryItems.join(' • ')}</p>
        </div>
    `;
}

// ENHANCED RESULTS DISPLAY - NOW WITH PARENT/CHILDREN SEPARATION ✨
function showResults() {
    document.querySelector('.question.active').classList.remove('active');
    document.getElementById('results').style.display = 'block';
    
    const allRecommendations = findMinistries();
    const resultsDiv = document.getElementById('ministry-recommendations');
    
    // CREATE SELECTIONS SUMMARY
    const selectionsHtml = createSelectionsummary();
    
    // Check if user IS a child - UPDATED FOR ELEMENTARY
    const userIsChild = ['infant', 'elementary', 'junior-high', 'high-school'].includes(answers.age);
    
    // SEPARATE ADULT AND CHILDREN'S MINISTRIES
    const { adultMinistries, childrenMinistries } = separateMinistries(allRecommendations);
    
    let html = selectionsHtml; // Add selections summary at top
    
    // If user IS a child, merge all ministries together
    if (userIsChild) {
        // Show all ministries together without separation
        const allMinistriesForChild = [...adultMinistries, ...childrenMinistries];
        
        allMinistriesForChild.forEach(ministry => {
            html += `
                <div class="ministry-item">
                    <h3>${ministry.name}</h3>
                    <p>${ministry.description}</p>
                    <p class="details">${ministry.details}</p>
                </div>
            `;
        });
    } else {
        // User is an adult - show separated sections
        
        // Add adult ministry recommendations
        if (adultMinistries.length > 0) {
            adultMinistries.forEach(ministry => {
                html += `
                    <div class="ministry-item">
                        <h3>${ministry.name}</h3>
                        <p>${ministry.description}</p>
                        <p class="details">${ministry.details}</p>
                    </div>
                `;
            });
        }
        
        // Add children's ministry section for adults (parents)
        if (childrenMinistries.length > 0) {
            html += `
                <div class="children-section">
                    <h2 class="children-header">For your children 👧👦</h2>
                    <div class="children-ministries">
            `;
            
            childrenMinistries.forEach(ministry => {
                html += `
                    <div class="ministry-item children-ministry">
                        <h3>${ministry.name}</h3>
                        <p>${ministry.description}</p>
                        <p class="details">${ministry.details}</p>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
    }
    
    resultsDiv.innerHTML = html;

    // Automatically scroll to the top so users start reading results immediately
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Add event handler for dynamically created "Go Back to Interests" button if it exists
    const backToInterestsBtn = document.querySelector('.nav-back-to-interests');
    if (backToInterestsBtn) {
        backToInterestsBtn.addEventListener('click', function() {
            goBack(5);
        });
    }
    
    // Update progress bar to 100%
    const progressBar = document.getElementById('progress-bar');
    if (progressBar) {
        progressBar.style.width = '100%';
    }
    const progressText = document.getElementById('progress-text');
    if (progressText) {
        progressText.textContent = 'Complete! 🎉';
    }
    
    // Submit anonymous analytics data
    submitAnalytics([...adultMinistries, ...childrenMinistries]);
    
    // Trigger confetti celebration!
    triggerConfetti();
}

// NEW FUNCTION - Separate adult and children's ministries
function separateMinistries(allMinistries) {
    const adultMinistries = [];
    const childrenMinistries = [];
    
    // Define children's age groups - UPDATED FOR ELEMENTARY
    const childrenAges = ['infant', 'elementary', 'junior-high', 'high-school'];
    const adultAges = ['college-young-adult', 'married-parents', 'journeying-adults'];
    
    allMinistries.forEach(ministry => {
        // Check if ministry is primarily for children
        const isChildrenMinistry = ministry.age && 
            ministry.age.some(age => childrenAges.includes(age)) &&
            !ministry.age.some(age => adultAges.includes(age));
        
        // Special cases for family ministries that serve adults but relate to children
        const isFamilyMinistry = ministry.name && (
            ministry.name.includes('Moms Group') ||
            ministry.name.includes('Meal Train') ||
            ministry.name.includes('Marriage Enrichment')
        );
        
        if (isChildrenMinistry) {
            childrenMinistries.push(ministry);
        } else {
            adultMinistries.push(ministry);
        }
    });
    
    return { adultMinistries, childrenMinistries };
}

function submitAnalytics(recommendations) {
    // Submit anonymous analytics for parish insights
    const analyticsData = {
        answers: answers,
        states: states,
        interests: interests,
        situation: situation,
        ministries: recommendations.map(m => m.name)
    };
    
    fetch('/api/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(analyticsData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Trigger background sync for PWA
            if (window.pwa && window.pwa.syncData) {
                window.pwa.syncData();
            }
        }
    })
    .catch(error => {
        // Don't show error to user for analytics
        // If offline, the service worker will handle the submission when back online
    });
}

// ENHANCED MINISTRY MATCHING FUNCTION - Fixed parent/children logic + MASS FIRST
function findMinistries() {
    // Normalize any array-like fields that may come as JSON strings
    const normalizeArray = (v) => {
        if (Array.isArray(v)) return v;
        if (typeof v === 'string') {
            try {
                const parsed = JSON.parse(v);
                return Array.isArray(parsed) ? parsed : [];
            } catch (e) {
                return [];
            }
        }
        return [];
    };

    const matches = [];
    const userAge = answers.age;
    const hasKidsInterest = interests.includes('kids');
    const isParent = states.includes('parent');
    
    // Remove debug logging
    
    // Check if ministries loaded
    if (!ministries || Object.keys(ministries).length === 0) {
        return [{
            name: 'Unable to Load Ministries',
            description: 'We apologize, but we cannot load the ministry list at this time.',
            details: 'Please contact the parish office at (615) 833-5520 or email <a href="mailto:support@stedward.org">support@stedward.org</a> for assistance.'
        }];
    }
    
    // Remove console.log
    
    for (const [key, ministry] of Object.entries(ministries)) {
        // Skip the welcome committee unless user specifically selected "new-to-stedward"
        if (key === 'welcome-committee' && !situation.includes('new-to-stedward')) {
            continue;
        }
        
        let isMatch = true;
        
        // ENHANCED LOGIC: If user selected "something for my children" or is a parent,
        // include children's ministries regardless of user's age
        const effectiveAges = [userAge];
        if (hasKidsInterest || isParent) {
            effectiveAges.push('infant', 'elementary', 'junior-high', 'high-school'); // UPDATED
        }
        
        // Check age (enhanced to include children's ages for parents)
        // Only apply age filtering if the ministry actually lists age groups.
        // An empty array should be treated as "all ages" rather than excluding it.
        if (ministry.age && ministry.age.length > 0 &&
            !ministry.age.some(age => effectiveAges.includes(age))) {
            isMatch = false;
        }
        
        // Normalize arrays
        ministry.age = normalizeArray(ministry.age);
        ministry.gender = normalizeArray(ministry.gender);
        ministry.state = normalizeArray(ministry.state);
        ministry.interest = normalizeArray(ministry.interest);
        ministry.situation = normalizeArray(ministry.situation);

        // Check gender (only if ministry specifies genders)
        if (ministry.gender && ministry.gender.length > 0 && answers.gender !== 'skip' && !ministry.gender.includes(answers.gender)) {
            isMatch = false;
        }
        
        // Check state - if ministry has state requirements, check if ANY selected state matches
        if (ministry.state && ministry.state.length > 0 && states.length > 0) {
            if (!states.includes('none-of-above')) {
                const hasMatchingState = ministry.state.some(s => states.includes(s));
                if (!hasMatchingState) {
                    isMatch = false;
                }
            }
        }
        
        // Check situation (if ministry has situation requirements)
        if (ministry.situation && ministry.situation.length > 0) {
            const hasMatchingSituation = ministry.situation.some(s => situation.includes(s));
            if (!hasMatchingSituation) {
                isMatch = false;
            }
        }
        
        // ENHANCED INTEREST MATCHING
        if (interests.length > 0) {
            // If user selected "all", they want to see EVERYTHING - don't filter by interests
            if (!interests.includes('all')) {
                // User has specific interests, check if ministry matches
                if (ministry.interest && ministry.interest.length > 0) {
                    let hasMatchingInterest = false;
                    
                    // If ministry has "all" interests, it matches ANY user interest selection
                    if (ministry.interest.includes('all')) {
                        hasMatchingInterest = true;
                    } else {
                        // Standard interest matching
                        hasMatchingInterest = ministry.interest.some(i => interests.includes(i));
                    }
                    
                    // SPECIAL CASE: If user selected "kids" interest, match children's ministries
                    if (!hasMatchingInterest && hasKidsInterest) {
                        // Check if this is a children's ministry - UPDATED FOR ELEMENTARY
                        const isChildrensMinistry = ministry.age && ministry.age.some(age => 
                            ['infant', 'elementary', 'junior-high', 'high-school'].includes(age)
                        );
                        if (isChildrensMinistry) {
                            hasMatchingInterest = true;
                        }
                    }
                    
                    if (!hasMatchingInterest) {
                        isMatch = false;
                    }
                }
            }
            // If user selected "all", isMatch remains whatever it was (true if age/gender/state matched)
        }
        
        if (isMatch) {
            matches.push(ministry);
            // Remove console.log
        } else {
            // Remove console.log
        }
    } // FIX: Added missing closing brace for the for loop
    
    // **CRITICAL FIX: ENSURE MASS IS ALWAYS FIRST**
    const massIndex = matches.findIndex(m => m.name === 'Come to Mass!');
    if (massIndex > 0) {
        const massMinistry = matches.splice(massIndex, 1)[0];
        matches.unshift(massMinistry);
    }
    
    // Enhanced fallback logic for parents
    if (matches.length === 0 && (isParent || hasKidsInterest)) {
        // Add key family-friendly ministries
        const familyMinistries = [
            ministries['st-edward-school'],
            ministries['prep-kids'],
            ministries['moms-group'],
            ministries['meal-train-provide'],
            ministries['totus-tuus-kids']
        ].filter(m => m); // Remove undefined ministries
        
        familyMinistries.forEach(ministry => {
            if (!matches.some(m => m.name === ministry.name)) {
                matches.push(ministry);
            }
        });
    }
    
    // Special handling for elementary - always show core options - UPDATED
    if (answers.age === 'elementary' && matches.length < 2) {
        // Always include these for elementary kids regardless of interest
        const coreKidsMinistries = [
            ministries['st-edward-school'],
            ministries['prep-kids'],
            ministries['mass']
        ];
        
        coreKidsMinistries.forEach(ministry => {
            if (ministry && !matches.some(m => m.name === ministry.name)) {
                matches.push(ministry);
            }
        });
        
        // Add Cub Scouts if they selected fellowship or all
        if (interests.includes('fellowship') || interests.includes('all')) {
            if (!matches.some(m => m.name === ministries['cub-scouts'].name)) {
                matches.push(ministries['cub-scouts']);
            }
        }
        
        // Ensure Mass is still first after adding core ministries
        const massIndex = matches.findIndex(m => m.name === 'Come to Mass!');
        if (massIndex > 0) {
            const massMinistry = matches.splice(massIndex, 1)[0];
            matches.unshift(massMinistry);
        }
    }
    
    // If no interests selected, show general options with navigation
    if (interests.length === 0) {
        const noInterestsMessage = {
            name: 'Select Your Interests',
            description: 'Please go back and select what interests you to see personalized recommendations.',
            details: '<button class="nav-btn nav-back-to-interests" style="margin-top: 10px;">← Go Back to Interests</button>'
        };
        return [noInterestsMessage];
    }
    
    // If we still have no matches for any age group, show general options
    if (matches.length === 0) {
        return [
            {
                name: 'Let\'s Connect You!',
                description: 'We have many opportunities that might interest you.',
                details: 'Please contact the parish office at (615) 833-5520 for personalized recommendations, or visit <a href="https://stedward.org" target="_blank">stedward.org</a> to explore all our ministries.'
            }
        ];
    }
    
    return matches;
}

function restart() {
    location.reload();
}

// CRITICAL FIX: Ensure question visibility is properly set on load
function initializeQuiz() {
    console.log('PWA: Initializing quiz...');
    
    // Hide all questions except the first one
    document.querySelectorAll('.question').forEach((q, index) => {
        if (index === 0) {
            q.classList.add('active');
            console.log('PWA: Showing question', index + 1);
        } else {
            q.classList.remove('active');
            console.log('PWA: Hiding question', index + 1);
        }
    });
    
    // Hide results - CRITICAL FIX
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.style.display = 'none';
        console.log('PWA: Hiding results section');
    } else {
        console.log('PWA: Results section not found');
    }
    
    // Initialize progress bar
    updateProgress();
    
    // Set up event handlers
    setupEventHandlers();
    
    // Load ministries and start the quiz
    loadMinistries().then(() => {
        console.log('PWA: Quiz initialization complete');
    }).catch((error) => {
        console.error('PWA: Quiz initialization failed:', error);
        // Fallback: hide loading overlay even if ministries fail to load
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            console.log('PWA: Fallback - hiding loading overlay');
            overlay.style.opacity = '0';
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 500);
        }
        
        // Set up fallback ministries data
        ministries = {
            'mass': {
                name: 'Come to Mass!',
                description: 'Join us for Mass and experience the heart of our community.',
                details: 'Mass times and information available at stedward.org'
            }
        };
        console.log('PWA: Using fallback ministries data');
    });
    
    // Fallback initialization after 5 seconds
    setTimeout(() => {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay && overlay.style.display !== 'none') {
            console.log('PWA: Fallback initialization - forcing quiz to start');
            overlay.style.opacity = '0';
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 500);
        }
    }, 5000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('PWA: DOMContentLoaded fired');
    try {
        initializeQuiz();
    } catch (error) {
        console.error('PWA: Error in DOMContentLoaded:', error);
        // Force hide loading overlay on error
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 500);
        }
    }
});

// Setup all event handlers
function setupEventHandlers() {
    console.log('PWA: Setting up event handlers...');
    
    try {
        // Header logo click
        const headerLogo = document.getElementById('headerLogo');
        if (headerLogo) {
            headerLogo.addEventListener('click', restart);
            console.log('PWA: Header logo handler set');
        }
        
        // Option buttons
        const optionButtons = document.querySelectorAll('.option-btn');
        console.log('PWA: Found', optionButtons.length, 'option buttons');
        
        optionButtons.forEach((btn, index) => {
            btn.addEventListener('click', function(e) {
                console.log('PWA: Option button clicked:', this.dataset.type, this.dataset.answer);
                const type = this.dataset.type;
                const answer = this.dataset.answer;
                answerQuestion(type, answer);
            });
        });
        
        // Navigation buttons
        const navBackButtons = document.querySelectorAll('.nav-back');
        console.log('PWA: Found', navBackButtons.length, 'nav-back buttons');
        
        navBackButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                console.log('PWA: Nav back clicked for question:', this.dataset.question);
                goBack(parseInt(this.dataset.question));
            });
        });
        
        const navNextState = document.querySelector('.nav-next-state');
        if (navNextState) {
            navNextState.addEventListener('click', nextFromState);
            console.log('PWA: Nav next state handler set');
        }
        
        const navNextSituation = document.querySelector('.nav-next-situation');
        if (navNextSituation) {
            navNextSituation.addEventListener('click', nextFromSituation);
            console.log('PWA: Nav next situation handler set');
        }
        
        const navShowResults = document.querySelector('.nav-show-results');
        if (navShowResults) {
            navShowResults.addEventListener('click', showResults);
            console.log('PWA: Nav show results handler set');
        }
        
        // State checkboxes
        const stateCheckboxes = document.querySelectorAll('#state-checkboxes .checkbox-clickable');
        console.log('PWA: Found', stateCheckboxes.length, 'state checkboxes');
        
        stateCheckboxes.forEach(item => {
            item.addEventListener('click', function(e) {
                if (e.target.type !== 'checkbox' && e.target.tagName !== 'LABEL') {
                    console.log('PWA: State checkbox clicked:', this.dataset.value);
                    toggleStateCheckbox(this.dataset.value);
                }
            });
        });
        
        document.querySelectorAll('#state-checkboxes input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', function() {
                console.log('PWA: State checkbox changed:', this.value);
                handleStateCheckboxChange(this.value);
            });
        });
        
        // Situation checkboxes
        const situationCheckboxes = document.querySelectorAll('#situation-checkboxes .checkbox-clickable');
        console.log('PWA: Found', situationCheckboxes.length, 'situation checkboxes');
        
        situationCheckboxes.forEach(item => {
            item.addEventListener('click', function(e) {
                if (e.target.type !== 'checkbox' && e.target.tagName !== 'LABEL') {
                    console.log('PWA: Situation checkbox clicked:', this.dataset.value);
                    toggleSituationCheckbox(this.dataset.value);
                }
            });
        });
        
        document.querySelectorAll('#situation-checkboxes input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', function() {
                console.log('PWA: Situation checkbox changed:', this.id);
                handleSituationCheckboxChange(this.id);
            });
        });
        
        // Restart button
        const restartBtn = document.querySelector('.btn-restart');
        if (restartBtn) {
            restartBtn.addEventListener('click', restart);
            console.log('PWA: Restart button handler set');
        }
        
        console.log('PWA: Event handlers setup complete');
    } catch (error) {
        console.error('PWA: Error setting up event handlers:', error);
    }
}

// Also initialize immediately in case DOMContentLoaded already fired
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeQuiz);
} else {
    initializeQuiz();
}

// REMOVED CONTACT FORM FUNCTIONS - NO PII COLLECTION
