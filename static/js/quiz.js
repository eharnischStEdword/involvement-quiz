// © 2024–2025 Harnisch LLC. All Rights Reserved.
// Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
// Unauthorized use, distribution, or modification is prohibited.

// Store user answers
const answers = {};
const situation = [];
const states = []; // Array for multiple state selections
const interests = []; // Array for multiple interests
let currentQuestion = 1;
const totalQuestions = 5;
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
        const response = await fetch('/api/get-ministries', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            timeout: 10000 // 10 second timeout
        });
        
        if (response.ok) {
            ministries = await response.json();
            console.log('Ministries loaded successfully');
            
            // Hide loading screen on success
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) {
                overlay.style.opacity = '0';
                setTimeout(() => {
                    overlay.style.display = 'none';
                }, 500);
            }
        } else {
            throw new Error(`Server error: ${response.status}`);
        }
    } catch (error) {
        console.error('Error loading ministries:', error);
        loadingRetries++;
        
        if (loadingRetries < maxRetries) {
            // Retry after a delay
            const retryDelay = loadingRetries * 2000; // 2s, 4s, 6s
            console.log(`Retrying in ${retryDelay/1000} seconds...`);
            
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
            showLoadingError();
        }
    }
}

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
    answers[type] = answer;
    
    // Update button styling
    const buttons = document.querySelectorAll(`#q${currentQuestion} .option-btn`);
    buttons.forEach(btn => btn.classList.remove('selected'));
    event.target.classList.add('selected');
    
    // Wait a moment for visual feedback
    setTimeout(() => {
        // For younger age groups, skip state in life question - UPDATED FOR ELEMENTARY
        if (type === 'age' && ['infant', 'elementary', 'junior-high', 'high-school'].includes(answer)) {
            states.push('single'); // Auto-assign single for younger ages
        }
        
        currentQuestion++;
        
        // Skip question 3 (state in life) for younger age groups - UPDATED FOR ELEMENTARY
        if (currentQuestion === 3 && answers.age && ['infant', 'elementary', 'junior-high', 'high-school'].includes(answers.age)) {
            currentQuestion = 4; // Jump to situation question
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

function nextFromSituation() {
    currentQuestion++;
    populateInterestOptions();
    updateProgress();
    showQuestion(currentQuestion);
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
    document.querySelectorAll('.question').forEach(q => q.classList.remove('active'));
    const targetQuestion = document.getElementById(`q${questionNum}`);
    if (targetQuestion) {
        targetQuestion.classList.add('active');
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
            console.log('Analytics submitted successfully');
        }
    })
    .catch(error => {
        console.log('Analytics submission failed:', error);
        // Don't show error to user for analytics
    });
}

// ENHANCED MINISTRY MATCHING FUNCTION - Fixed parent/children logic + MASS FIRST
function findMinistries() {
    const matches = [];
    const userAge = answers.age;
    const hasKidsInterest = interests.includes('kids');
    const isParent = states.includes('parent');
    
    // Check if ministries loaded
    if (!ministries || Object.keys(ministries).length === 0) {
        return [{
            name: 'Unable to Load Ministries',
            description: 'We apologize, but we cannot load the ministry list at this time.',
            details: 'Please contact the parish office at (615) 833-5520 or email <a href="mailto:support@stedward.org">support@stedward.org</a> for assistance.'
        }];
    }
    
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
        if (ministry.age && !ministry.age.some(age => effectiveAges.includes(age))) {
            isMatch = false;
        }
        
        // Check gender (if specified and not skipped)
        if (ministry.gender && answers.gender !== 'skip' && !ministry.gender.includes(answers.gender)) {
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
        if (interests.length > 0 && !interests.includes('all') && ministry.interest) {
            let hasMatchingInterest = false;
            
            // Standard interest matching
            hasMatchingInterest = ministry.interest.some(i => interests.includes(i));
            
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
        
        if (isMatch) {
            matches.push(ministry);
        }
    }
    
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
    // Hide all questions except the first one
    document.querySelectorAll('.question').forEach((q, index) => {
        if (index === 0) {
            q.classList.add('active');
        } else {
            q.classList.remove('active');
        }
    });
    
    // Hide results
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.style.display = 'none';
    }
    
    // Initialize progress bar
    updateProgress();
    
    // Start loading ministries
    loadMinistries();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeQuiz();
    setupEventHandlers();
});

// Setup all event handlers
function setupEventHandlers() {
    // Header logo click
    document.getElementById('headerLogo').addEventListener('click', restart);
    
    // Option buttons
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const type = this.dataset.type;
            const answer = this.dataset.answer;
            answerQuestion(type, answer);
        });
    });
    
    // Navigation buttons
    document.querySelectorAll('.nav-back').forEach(btn => {
        btn.addEventListener('click', function() {
            goBack(parseInt(this.dataset.question));
        });
    });
    
    document.querySelector('.nav-next-state').addEventListener('click', nextFromState);
    document.querySelector('.nav-next-situation').addEventListener('click', nextFromSituation);
    document.querySelector('.nav-show-results').addEventListener('click', showResults);
    
    // State checkboxes
    document.querySelectorAll('#state-checkboxes .checkbox-clickable').forEach(item => {
        item.addEventListener('click', function(e) {
            if (e.target.type !== 'checkbox' && e.target.tagName !== 'LABEL') {
                toggleStateCheckbox(this.dataset.value);
            }
        });
    });
    
    document.querySelectorAll('#state-checkboxes input[type="checkbox"]').forEach(cb => {
        cb.addEventListener('change', function() {
            handleStateCheckboxChange(this.value);
        });
    });
    
    // Situation checkboxes
    document.querySelectorAll('#situation-checkboxes .checkbox-clickable').forEach(item => {
        item.addEventListener('click', function(e) {
            if (e.target.type !== 'checkbox' && e.target.tagName !== 'LABEL') {
                toggleSituationCheckbox(this.dataset.value);
            }
        });
    });
    
    document.querySelectorAll('#situation-checkboxes input[type="checkbox"]').forEach(cb => {
        cb.addEventListener('change', function() {
            handleSituationCheckboxChange(this.id);
        });
    });
    
    // Contact form buttons
    document.querySelector('.btn-show-contact').addEventListener('click', showContactForm);
    document.querySelector('.btn-skip-contact').addEventListener('click', skipContact);
    document.querySelector('.btn-hide-contact').addEventListener('click', hideContactForm);
    document.querySelector('.btn-hide-contact-success').addEventListener('click', hideContactForm);
    
    // Contact form submission
    document.getElementById('userContactForm').addEventListener('submit', submitContact);
    
    // Restart button
    document.querySelector('.btn-restart').addEventListener('click', restart);
}

// Also initialize immediately in case DOMContentLoaded already fired
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeQuiz);
} else {
    initializeQuiz();
    setupEventHandlers();
}

function showContactForm() {
    document.querySelector('.contact-form-toggle').style.display = 'none';
    document.getElementById('contactForm').style.display = 'block';
}

function hideContactForm() {
    document.querySelector('.contact-form-toggle').style.display = 'flex';
    document.getElementById('contactForm').style.display = 'none';
    document.getElementById('contactSuccess').style.display = 'none';
    document.getElementById('userContactForm').style.display = 'block';
    document.getElementById('userContactForm').reset();
}

function skipContact() {
    document.getElementById('contactFormSection').style.display = 'none';
}

function submitContact(event) {
    event.preventDefault();
    
    const form = document.getElementById('userContactForm');
    const submitBtn = document.getElementById('submitContactBtn');
    const formData = new FormData(form);
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
    
    const contactData = {
        name: formData.get('name'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        message: formData.get('message'),
        quiz_results: {
            answers: answers,
            states: states,
            interests: interests,
            situation: situation,
            recommended_ministries: findMinistries().map(m => m.name)
        }
    };
    
    fetch('/api/submit-contact', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(contactData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('userContactForm').style.display = 'none';
            document.getElementById('contactSuccess').style.display = 'block';
        } else {
            alert('There was an issue submitting your information. Please try again or call (615) 833-5520.');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span class="btn-icon">📧</span> Send My Information';
        }
    })
    .catch(error => {
        console.error('Contact form error:', error);
        alert('There was a network error. Please try again or call (615) 833-5520.');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="btn-icon">📧</span> Send My Information';
    });
}
