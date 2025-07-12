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

// SIMPLIFIED MINISTRY MATCHING - REWRITTEN FROM SCRATCH
function findMinistries() {
    const matches = [];
    const userAge = answers.age;
    const userGender = answers.gender;
    const showEverything = interests.includes('all');
    
    console.log('Finding ministries for:', {
        age: userAge,
        gender: userGender,
        states: states,
        interests: interests,
        situation: situation,
        showEverything: showEverything
    });
    
    // Check if ministries loaded
    if (!ministries || Object.keys(ministries).length === 0) {
        return [{
            name: 'Unable to Load Ministries',
            description: 'We apologize, but we cannot load the ministry list at this time.',
            details: 'Please contact the parish office at (615) 833-5520 or email <a href="mailto:support@stedward.org">support@stedward.org</a> for assistance.'
        }];
    }
    
    // Loop through all ministries
    for (const [key, ministry] of Object.entries(ministries)) {
        let shouldInclude = false;
        
        // STEP 1: Check if ministry is age-appropriate
        const isAgeAppropriate = !ministry.age || ministry.age.length === 0 || ministry.age.includes(userAge);
        
        // STEP 2: Check gender if specified
        const isGenderAppropriate = !ministry.gender || ministry.gender.length === 0 || 
                                   userGender === 'skip' || ministry.gender.includes(userGender);
        
        // STEP 3: Check state requirements
        const hasStateRequirement = ministry.state && ministry.state.length > 0;
        const meetsStateRequirement = !hasStateRequirement || 
                                    states.some(s => ministry.state.includes(s));
        
        // STEP 4: Check situation requirements
        const hasSituationRequirement = ministry.situation && ministry.situation.length > 0;
        const meetsSituationRequirement = !hasSituationRequirement || 
                                         situation.some(s => ministry.situation.includes(s));
        
        // Basic eligibility check
        if (isAgeAppropriate && isGenderAppropriate && meetsStateRequirement && meetsSituationRequirement) {
            // Now check interests
            if (showEverything) {
                // User wants everything - include this ministry
                shouldInclude = true;
            } else if (interests.length === 0) {
                // No interests selected - shouldn't happen but include if eligible
                shouldInclude = true;
            } else {
                // Check if ministry matches any selected interests
                if (!ministry.interest || ministry.interest.length === 0) {
                    // Ministry has no interest requirements - include it
                    shouldInclude = true;
                } else if (ministry.interest.includes('all')) {
                    // Ministry is for everyone - include it
                    shouldInclude = true;
                } else {
                    // Check if any ministry interests match user interests
                    shouldInclude = ministry.interest.some(i => interests.includes(i));
                }
                
                // Special case: parent looking for kids programs
                if (!shouldInclude && interests.includes('kids')) {
                    const childAges = ['infant', 'elementary', 'junior-high', 'high-school'];
                    if (ministry.age && ministry.age.some(a => childAges.includes(a))) {
                        shouldInclude = true;
                    }
                }
            }
        }
        
        if (shouldInclude) {
            matches.push(ministry);
            console.log('✓ Matched:', ministry.name);
        }
    }
    
    // Ensure Mass is always first
    const massIndex = matches.findIndex(m => m.name === 'Come to Mass!');
    if (massIndex > 0) {
        const massMinistry = matches.splice(massIndex, 1)[0];
        matches.unshift(massMinistry);
    }
    
    console.log(`Total ministries matched: ${matches.length}`);
    
    // Fallback if no matches
    if (matches.length === 0) {
        return [{
            name: 'Let\'s Connect You!',
            description: 'We have many opportunities that might interest you.',
            details: 'Please contact the parish office at (615) 833-5520 for personalized recommendations, or visit <a href="https://stedward.org" target="_blank">stedward.org</a> to explore all our ministries.'
        }];
    }
    
    return matches;
}

// SIMPLIFIED MINISTRY SEPARATION
function separateMinistries(allMinistries) {
    const adultMinistries = [];
    const childrenMinistries = [];
    
    const childAges = ['infant', 'elementary', 'junior-high', 'high-school'];
    const adultAges = ['college-young-adult', 'married-parents', 'journeying-adults'];
    
    allMinistries.forEach(ministry => {
        // A ministry is "children's" if it ONLY serves children ages
        const servesOnlyChildren = ministry.age && 
                                 ministry.age.length > 0 &&
                                 ministry.age.every(age => childAges.includes(age));
        
        if (servesOnlyChildren) {
            childrenMinistries.push(ministry);
        } else {
            adultMinistries.push(ministry);
        }
    });
    
    return { adultMinistries, childrenMinistries };
}

// RESULTS DISPLAY
function showResults() {
    document.querySelector('.question.active').classList.remove('active');
    document.getElementById('results').style.display = 'block';
    
    const allRecommendations = findMinistries();
    const resultsDiv = document.getElementById('ministry-recommendations');
    
    // Create selections summary
    const selectionsHtml = createSelectionsummary();
    
    // Check if user is a child
    const userIsChild = ['infant', 'elementary', 'junior-high', 'high-school'].includes(answers.age);
    
    let html = selectionsHtml;
    
    if (userIsChild) {
        // Child user - show all ministries together
        allRecommendations.forEach(ministry => {
            html += `
                <div class="ministry-item">
                    <h3>${ministry.name}</h3>
                    <p>${ministry.description}</p>
                    <p class="details">${ministry.details}</p>
                </div>
            `;
        });
    } else {
        // Adult user - separate adult and children's ministries
        const { adultMinistries, childrenMinistries } = separateMinistries(allRecommendations);
        
        // Show adult ministries first
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
        
        // Show children's ministries in separate section
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
    submitAnalytics(allRecommendations);
    
    // Trigger confetti celebration!
    triggerConfetti();
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
