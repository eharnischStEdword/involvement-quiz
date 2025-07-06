// Fixed portions of quiz.js - Enhanced parent/children logic + selections summary

// 1. ENHANCED INTEREST OPTIONS - Add "something for my kids" option for parents
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

// 2. ENHANCED MINISTRY MATCHING FUNCTION - Fixed parent/children logic
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
    
    // If still no matches, show general guidance
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

// 3. ENHANCED RESULTS DISPLAY - Add selections summary
function showResults() {
    document.querySelector('.question.active').classList.remove('active');
    document.getElementById('results').style.display = 'block';
    
    const recommendations = findMinistries();
    const resultsDiv = document.getElementById('ministry-recommendations');
    
    // CREATE SELECTIONS SUMMARY
    const selectionsHtml = createSelectionsummary();
    
    let html = selectionsHtml; // Add selections summary at top
    
    // Add ministry recommendations
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
    
    // Submit anonymous analytics data
    submitAnalytics(recommendations);
    
    // Trigger confetti celebration!
    triggerConfetti();
}

// 4. NEW FUNCTION - Create selections summary
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
