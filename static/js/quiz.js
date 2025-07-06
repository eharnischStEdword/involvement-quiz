// Store user answers
const answers = {};
const situation = [];
const states = []; // Array for multiple state selections
const interests = []; // Array for multiple interests
let currentQuestion = 1;
const totalQuestions = 5;

// ENHANCED Age-specific interest options with "Something for my children"
const interestOptions = {
    infant: [
        { value: 'support', label: 'Parent Support & Community' },
        { value: 'education', label: 'Learning About Faith' },
        { value: 'service', label: 'Helping Others' },
        { value: 'all', label: 'Show me everything!' }
    ],
    kid: [
        { value: 'education', label: 'Learning & Growing in Faith' },
        { value: 'fellowship', label: 'Making Friends' },
        { value: 'music', label: 'Music & Arts' },
        { value: 'service', label: 'Helping Others' },
        { value: 'all', label: 'Show me everything!' }
    ],
    'junior-high': [
        { value: 'fellowship', label: 'Fellowship & Community' },
        { value: 'education', label: 'Learning & Teaching' },
        { value: 'service', label: 'Serving Others' },
        { value: 'prayer', label: 'Prayer & Worship' },
        { value: 'all', label: 'Show me everything!' }
    ],
    'high-school': [
        { value: 'fellowship', label: 'Fellowship & Community' },
        { value: 'service', label: 'Serving Others' },
        { value: 'prayer', label: 'Prayer & Worship' },
        { value: 'music', label: 'Music & Arts' },
        { value: 'education', label: 'Learning & Teaching' },
        { value: 'all', label: 'Show me everything!' }
    ],
    'college-young-adult': [
        { value: 'fellowship', label: 'Fellowship & Community' },
        { value: 'service', label: 'Serving Others' },
        { value: 'prayer', label: 'Prayer & Worship' },
        { value: 'education', label: 'Learning & Teaching' },
        { value: 'music', label: 'Music & Arts' },
        { value: 'all', label: 'Show me everything!' }
    ],
    'married-parents': [
        { value: 'fellowship', label: 'Fellowship & Community' },
        { value: 'service', label: 'Serving Others' },
        { value: 'education', label: 'Learning & Teaching' },
        { value: 'prayer', label: 'Prayer & Worship' },
        { value: 'support', label: 'Family Support' },
        { value: 'kids', label: 'Something for my children' }, // NEW OPTION
        { value: 'all', label: 'Show me everything!' }
    ],
    'journeying-adults': [
        { value: 'prayer', label: 'Prayer & Worship' },
        { value: 'service', label: 'Serving Others' },
        { value: 'fellowship', label: 'Fellowship & Community' },
        { value: 'education', label: 'Learning & Teaching' },
        { value: 'music', label: 'Music & Arts' },
        { value: 'kids', label: 'Something for my children' }, // NEW OPTION
        { value: 'all', label: 'Show me everything!' }
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
        // For younger age groups, skip state in life question
        if (type === 'age' && ['infant', 'kid', 'junior-high', 'high-school'].includes(answer)) {
            states.push('single'); // Auto-assign single for younger ages
        }
        
        currentQuestion++;
        
        // Skip question 3 (state in life) for younger age groups
        if (currentQuestion === 3 && answers.age && ['infant', 'kid', 'junior-high', 'high-school'].includes(answers.age)) {
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
    // Only handle if click came from the container, not the checkbox or label
    if (event.target.type === 'checkbox' || event.target.tagName === 'LABEL') {
        return; // Let the native behavior handle it
    }
    
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
    // Only handle if click came from the container, not the checkbox or label
    if (event.target.type === 'checkbox' || event.target.tagName === 'LABEL') {
        return; // Let the native behavior handle it
    }
    
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
        checkboxDiv.className = 'checkbox-item';
        checkboxDiv.onclick = () => toggleInterestCheckbox(option.value);
        
        checkboxDiv.innerHTML = `
            <input type="checkbox" id="interest-${option.value}" value="${option.value}" onchange="handleInterestCheckboxChange('${option.value}')">
            <label for="interest-${option.value}">${option.label}</label>
        `;
        
        interestContainer.appendChild(checkboxDiv);
    });
}

function toggleInterestCheckbox(value) {
    // Only handle if click came from the container, not the checkbox or label
    if (event.target.type === 'checkbox' || event.target.tagName === 'LABEL') {
        return; // Let the native behavior handle it
    }
    
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
    
    // Handle going back when state question was skipped
    if (questionNum === 4 && answers.age && ['infant', 'kid', 'junior-high', 'high-school'].includes(answers.age)) {
        currentQuestion = 2; // Go back to gender question
    } else if (questionNum === 5 && answers.age && ['infant', 'kid', 'junior-high', 'high-school'].includes(answers.age)) {
        currentQuestion = 4; // Go back to situation question
    } else {
        currentQuestion = questionNum - 1;
    }
    
    updateProgress();
    showQuestion(currentQuestion);
}

function showQuestion(questionNum) {
    document.querySelectorAll('.question').forEach(q => q.classList.remove('active'));
    document.getElementById(`q${questionNum}`).classList.add('active');
}

function updateProgress() {
    let totalQuestionsForUser = totalQuestions;
    // If younger age group, they skip state question, so only 4 questions total
    if (answers.age && ['infant', 'kid', 'junior-high', 'high-school'].includes(answers.age)) {
        totalQuestionsForUser = 4;
    }
    
    let progressQuestions = currentQuestion - 1;
    // Adjust for skipped question
    if (currentQuestion >= 4 && answers.age && ['infant', 'kid', 'junior-high', 'high-school'].includes(answers.age)) {
        progressQuestions = currentQuestion - 2; // Account for skipped state question
    }
    
    const progress = Math.min(progressQuestions / totalQuestionsForUser * 100, 100);
    document.getElementById('progress-bar').style.width = progress + '%';
}

// NEW FUNCTION - Create selections summary
function createSelectionsummary() {
    const summaryItems = [];
    
    // Age group
    if (answers.age) {
        const ageLabels = {
            'infant': 'Infant (0-3)',
            'kid': 'Kid (PreK-Grade 5)', 
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
            'just-curious': 'Just Curious'
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
            <h3>Your Selections:</h3>
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
    
    // Check if user IS a child
    const userIsChild = ['infant', 'kid', 'junior-high', 'high-school'].includes(answers.age);
    
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
    
    // Update progress bar to 100%
    document.getElementById('progress-bar').style.width = '100%';
    
    // Submit anonymous analytics data
    submitAnalytics([...adultMinistries, ...childrenMinistries]);
    
    // Trigger confetti celebration!
    triggerConfetti();
}

// NEW FUNCTION - Separate adult and children's ministries
function separateMinistries(allMinistries) {
    const adultMinistries = [];
    const childrenMinistries = [];
    
    // Define children's age groups
    const childrenAges = ['infant', 'kid', 'junior-high', 'high-school'];
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

// ENHANCED MINISTRY MATCHING FUNCTION - Fixed parent/children logic
function findMinistries() {
    const matches = [];
    const userAge = answers.age;
    const hasKidsInterest = interests.includes('kids');
    const isParent = states.includes('parent');
    
    for (const [key, ministry] of Object.entries(ministries)) {
        let isMatch = true;
        
        // ENHANCED LOGIC: If user selected "something for my children" or is a parent,
        // include children's ministries regardless of user's age
        const effectiveAges = [userAge];
        if (hasKidsInterest || isParent) {
            effectiveAges.push('infant', 'kid', 'junior-high', 'high-school');
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
                // Check if this is a children's ministry
                const isChildrensMinistry = ministry.age && ministry.age.some(age => 
                    ['infant', 'kid', 'junior-high', 'high-school'].includes(age)
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
    
    // Special handling for kids - always show core options
    if (answers.age === 'kid' && matches.length < 2) {
        // Always include these for kids regardless of interest
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
    }
    
    // If no interests selected, show general options
    if (interests.length === 0) {
        return [
            {
                name: 'Select Your Interests',
                description: 'Please go back and select what interests you to see personalized recommendations.',
                details: 'Use the back button to choose your areas of interest.'
            }
        ];
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

// Initialize progress bar
updateProgress();

// Hide loading overlay once page is fully loaded
window.addEventListener('load', function() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(() => {
            overlay.style.display = 'none';
        }, 500);
    }
});
