// St. Edward Ministry Finder - Quiz Logic

// Store user answers
const answers = {};
const situation = [];
const interests = []; // New array for multiple interests
let currentQuestion = 1;
const totalQuestions = 5;

// Age-specific interest options
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
        { value: 'all', label: 'Show me everything!' }
    ],
    'journeying-adults': [
        { value: 'prayer', label: 'Prayer & Worship' },
        { value: 'service', label: 'Serving Others' },
        { value: 'fellowship', label: 'Fellowship & Community' },
        { value: 'education', label: 'Learning & Teaching' },
        { value: 'music', label: 'Music & Arts' },
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
            answers['state'] = 'single'; // Auto-assign single for younger ages
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

function toggleSituationCheckbox(value) {
    // Only handle if click came from the container, not the checkbox or label
    if (event.target.type === 'checkbox' || event.target.tagName === 'LABEL') {
        return; // Let the native behavior handle it
    }
    
    const checkbox = document.getElementById(value);
    checkbox.checked = !checkbox.checked;
    
    // Trigger the change handler
    handleCheckboxChange(value);
}

function handleCheckboxChange(value) {
    const checkbox = document.getElementById(value);
    const item = checkbox.parentElement;
    
    // Handle "none of above" logic
    if (value === 'none-of-above') {
        if (checkbox.checked) {
            // Clear all other checkboxes
            document.querySelectorAll('#situation-checkboxes input[type="checkbox"]').forEach(cb => {
                if (cb.id !== 'none-of-above') {
                    cb.checked = false;
                    cb.parentElement.classList.remove('selected');
                }
            });
            situation.length = 0; // Clear array
            situation.push('none-of-above');
        }
    } else {
        // If selecting something else, uncheck "none of above"
        const noneCheckbox = document.getElementById('none-of-above');
        if (noneCheckbox && noneCheckbox.checked) {
            noneCheckbox.checked = false;
            noneCheckbox.parentElement.classList.remove('selected');
            const noneIndex = situation.indexOf('none-of-above');
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
    
    // Clear interests array if going back from results
    if (questionNum === 5) {
        interests.length = 0;
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

function showResults() {
    document.querySelector('.question.active').classList.remove('active');
    document.getElementById('results').style.display = 'block';
    
    const recommendations = findMinistries();
    const resultsDiv = document.getElementById('ministry-recommendations');
    
    let html = '';
    recommendations.forEach(ministry => {
        html += `
            <div class="ministry-item">
                <h3>${ministry.name}</h3>
                <p>${ministry.description}</p>
                <p class="details">${ministry.details}</p>
            </div>
        `;
    });
    resultsDiv.innerHTML = html;
    
    // Update progress bar to 100%
    document.getElementById('progress-bar').style.width = '100%';
    
    // Trigger confetti celebration!
    triggerConfetti();
}

function findMinistries() {
    const matches = [];
    
    for (const [key, ministry] of Object.entries(window.ministries)) {
        let isMatch = true;
        
        // Check age
        if (ministry.age && !ministry.age.includes(answers.age)) {
            isMatch = false;
        }
        
        // Check gender (if specified and not skipped)
        if (ministry.gender && answers.gender !== 'skip' && !ministry.gender.includes(answers.gender)) {
            isMatch = false;
        }
        
        // Check state (if specified and not skipped)
        if (ministry.state && answers.state !== 'skip' && !ministry.state.includes(answers.state)) {
            isMatch = false;
        }
        
        // Check situation (if ministry has situation requirements)
        if (ministry.situation && ministry.situation.length > 0) {
            const hasMatchingSituation = ministry.situation.some(s => situation.includes(s));
            if (!hasMatchingSituation) {
                isMatch = false;
            }
        }
        
        // Check interests (support multiple selections)
        if (interests.length > 0 && !interests.includes('all') && ministry.interest) {
            const hasMatchingInterest = ministry.interest.some(i => interests.includes(i));
            if (!hasMatchingInterest) {
                isMatch = false;
            }
        }
        
        if (isMatch) {
            matches.push(ministry);
        }
    }
    
    // Special handling for kids - always show core options
    if (answers.age === 'kid' && matches.length < 2) {
        // Always include these for kids regardless of interest
        const coreKidsMinistries = [
            window.ministries['st-edward-school'],
            window.ministries['prep-kids'],
            window.ministries['mass']
        ];
        
        coreKidsMinistries.forEach(ministry => {
            if (ministry && !matches.some(m => m.name === ministry.name)) {
                matches.push(ministry);
            }
        });
        
        // Add Cub Scouts if they selected fellowship or all
        if (interests.includes('fellowship') || interests.includes('all')) {
            if (!matches.some(m => m.name === window.ministries['cub-scouts'].name)) {
                matches.push(window.ministries['cub-scouts']);
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
                name: 'Parish Community',
                description: 'We have many opportunities to get involved!',
                details: 'Please contact the parish office at (615) 833-5520 for personalized recommendations.'
            }
        ];
    }
    
    return matches;
}

function restart() {
    location.reload();
}

// Initialize progress bar
window.addEventListener('DOMContentLoaded', function() {
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
});
