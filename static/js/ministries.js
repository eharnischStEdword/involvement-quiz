// St. Edward Ministry Database
// This file contains all ministry information
// Later we can load this from an API instead of hardcoding

window.ministries = {
    // Sacraments
    'ocia': {
        name: 'OCIA (Adult Baptism/Full Communion)',
        description: 'Program that prepares adults for Baptism, Holy Communion & Confirmation',
        details: 'Visit <a href="https://stedward.org/ocia" target="_blank">stedward.org/ocia</a> for more information',
        age: ['college-young-adult', 'married-parents', 'journeying-adults'],
        interest: ['education', 'prayer']
    },
    'infant-baptism': {
        name: 'Infant Baptism (0-5 yrs)',
        description: 'Baptism preparation for families with young children',
        details: 'Visit <a href="https://stedward.org/baptism" target="_blank">stedward.org/baptism</a> to register',
        age: ['infant'],
        interest: ['education', 'prayer', 'all']
    },
    'marriage-convalidation': {
        name: 'Marriage Convalidation',
        description: 'Sacrament of Holy Matrimony for civilly married couples',
        details: 'Fill out intake form at <a href="https://stedward.org/marriage-prep" target="_blank">stedward.org/marriage-prep</a>',
        age: ['college-young-adult', 'married-parents'],
        state: ['married'],
        interest: ['education', 'prayer']
    },
    
    // Parent Support
    'moms-group': {
        name: 'Moms Group',
        description: 'Spiritual & practical support for mothers with rosary walks and monthly brunch',
        details: 'Join on Flocknote: <a href="https://stedwardnash.flocknote.com/signup/180620" target="_blank">stedwardnash.flocknote.com/signup/180620</a><br>Or join GroupMe: <a href="https://groupme.com/join_group/107457911/mdAevstX" target="_blank">groupme.com/join_group/107457911/mdAevstX</a>',
        age: ['infant', 'married-parents'],
        gender: ['female'],
        state: ['parent'],
        interest: ['fellowship', 'support', 'prayer']
    },
    'meal-train-receive': {
        name: 'Meal Train Support for Your Family',
        description: 'We want to serve you and support you with our meal train for families with new members!',
        details: 'Contact <a href="mailto:elizabethlansden@gmail.com">elizabethlansden@gmail.com</a> if your family is growing soon and would like to receive meals.',
        age: ['infant'],
        interest: ['support', 'fellowship', 'all']
    },
    'meal-train-provide': {
        name: 'Meal Train for New Families',
        description: 'Support growing families with meal delivery when they welcome a baby, adopt, or receive a foster child',
        details: 'Flexible commitment - participate 1-3 times per year. Contact <a href="mailto:elizabethlansden@gmail.com">elizabethlansden@gmail.com</a> to join the volunteer list.',
        age: ['married-parents', 'college-young-adult', 'journeying-adults'],
        interest: ['service', 'fellowship', 'support']
    },
    
    // Kids
    'st-edward-school': {
        name: 'St. Edward School (PreK-8th Grade)',
        description: 'Catholic education in a faith-filled community environment',
        details: 'Apply for enrollment: <a href="https://ses.stedward.org/apply" target="_blank">ses.stedward.org/apply</a>',
        age: ['kid'],
        interest: ['education', 'fellowship', 'all']
    },
    'cub-scouts': {
        name: 'Cub Scouts',
        description: 'Character development and outdoor adventures for boys and girls',
        details: 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for more information',
        age: ['kid'],
        interest: ['fellowship', 'service', 'all']
    },
    'catechesis': {
        name: 'Catechesis of the Good Shepherd Atrium',
        description: 'Montessori-based religious education for Pre-K-2',
        details: 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for enrollment',
        age: ['kid'],
        interest: ['education', 'prayer']
    },
    'prep-kids': {
        name: 'PREP - Sunday Religious Ed',
        description: 'Including First Confession & First Holy Communion prep',
        details: 'Visit <a href="https://stedward.org/prep" target="_blank">stedward.org/prep</a> to register',
        age: ['kid'],
        interest: ['education', 'prayer']
    },
    'totus-tuus-kids': {
        name: 'Totus Tuus Summer Program (Grades 1-6)',
        description: 'Week-long summer catechetical program with games and activities',
        details: 'Visit <a href="https://stedward.org/totus-tuus" target="_blank">stedward.org/totus-tuus</a> - registration opens in spring',
        age: ['kid'],
        interest: ['education', 'fellowship', 'prayer']
    },
    
    // Junior High
    'prep-jr': {
        name: 'PREP - Sacrament Prep & Faith Formation',
        description: 'Religious education and sacrament preparation',
        details: 'Visit <a href="https://stedward.org/prep" target="_blank">stedward.org/prep</a> to register',
        age: ['junior-high'],
        interest: ['education', 'prayer']
    },
    'fraternus-jr': {
        name: 'Fraternus',
        description: 'Brotherhood & virtue formation for boys - developing Catholic men through weekly meetings and excursions',
        details: 'Wednesdays 6:00-8:00pm. Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for information',
        age: ['junior-high'],
        gender: ['male'],
        interest: ['fellowship', 'education']
    },
    'fidelis-jr': {
        name: 'Fidelis',
        description: 'Sisterhood & virtue for girls - faith-filled friendships through discussion, activities, and fun',
        details: 'Bi-weekly Wednesdays 6:30-8:30pm. Contact <a href="mailto:fidelisnashville@gmail.com">fidelisnashville@gmail.com</a>',
        age: ['junior-high'],
        gender: ['female'],
        interest: ['fellowship', 'education']
    },
    'totus-tuus-jr': {
        name: 'Totus Tuus Summer Program',
        description: 'Summer catechetical program with peer ministry opportunities',
        details: 'Visit <a href="https://stedward.org/totus-tuus" target="_blank">stedward.org/totus-tuus</a> - registration opens in spring',
        age: ['junior-high'],
        interest: ['education', 'fellowship', 'prayer']
    },
    
    // High School
    'fraternus-hs': {
        name: 'Fraternus',
        description: 'Weekly formation, excursions, and retreats developing virtuous Catholic men',
        details: 'Wednesdays 6:00-8:00pm with 4 weekend excursions. Contact <a href="mailto:support@stedward.org">support@stedward.org</a>',
        age: ['high-school'],
        gender: ['male'],
        interest: ['fellowship', 'education']
    },
    'fidelis-hs': {
        name: 'Fidelis',
        description: 'Weekly formation, excursions, and retreats for young women in faith',
        details: 'Bi-weekly Wednesdays 6:30-8:30pm. Contact <a href="mailto:fidelisnashville@gmail.com">fidelisnashville@gmail.com</a>',
        age: ['high-school'],
        gender: ['female'],
        interest: ['fellowship', 'education']
    },
    'liturgical-hs': {
        name: 'Liturgical Ministries (Age 16+)',
        description: 'Serve as lector, hospitality, or EMHC',
        details: 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for training',
        age: ['high-school'],
        interest: ['service', 'prayer']
    },
    'choir-hs': {
        name: 'Sacred Music / Choir (Age 16+)',
        description: 'Weekly rehearsal & Mass service',
        details: 'Fill out form: <a href="https://forms.office.com/Pages/ResponsePage.aspx?id=spbPjOu3C0enFewWltg-vSGAojmE4WpCvxL72BS8279UN0RYT042M0dDNlNLQ0ZTSDlFQ1ZWMTdKWC4u" target="_blank">Sacred Music Interest Form</a><br>Or contact <a href="mailto:nrankin@stedward.org">nrankin@stedward.org</a>',
        age: ['high-school'],
        interest: ['music', 'prayer']
    },
    'totus-tuus-hs': {
        name: 'Totus Tuus Summer Program',
        description: 'Apologetics & fellowship for high schoolers with leadership opportunities',
        details: 'Visit <a href="https://stedward.org/totus-tuus" target="_blank">stedward.org/totus-tuus</a> - registration opens in spring',
        age: ['high-school'],
        interest: ['education', 'fellowship', 'prayer']
    },
    
    // College & Young Adult
    'theology-tap': {
        name: 'Theology on Tap (Summer Series)',
        description: 'Faith & fellowship in beer-garden setting with engaging speakers',
        details: 'Visit <a href="https://stedward.org/theo-on-tap" target="_blank">stedward.org/theo-on-tap</a> - check bulletin for dates',
        age: ['college-young-adult'],
        interest: ['fellowship', 'education']
    },
    'totus-tuus-missionary': {
        name: 'Totus Tuus Missionary Teams',
        description: 'Summer evangelization work teaching children and teens',
        details: 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for application',
        age: ['college-young-adult'],
        interest: ['service', 'education', 'prayer']
    },
    'fraternus-mentors': {
        name: 'Fraternus Adult Mentors',
        description: 'College men serve younger boys (Wednesday evenings)',
        details: 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for information',
        age: ['college-young-adult'],
        gender: ['male'],
        interest: ['service', 'fellowship']
    },
    'ocia-sponsors': {
        name: 'OCIA Sponsors',
        description: 'Accompany adults entering the Church',
        details: 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for information',
        age: ['college-young-adult'],
        interest: ['service', 'education']
    },
    'room-inn-ya': {
        name: 'Room-in-the-Inn Shelter Crew',
        description: 'Saturday-night hospitality for homeless men during winter months',
        details: 'Contact Greg Beem at <a href="mailto:support@stedward.org">support@stedward.org</a>',
        age: ['college-young-adult'],
        interest: ['service']
    },
    'cursillo': {
        name: 'Cursillo Retreats',
        description: 'Three-day renewal weekends focused on spiritual growth',
        details: 'Visit <a href="https://stedward.org/cursillo" target="_blank">stedward.org/cursillo</a> for information',
        age: ['college-young-adult'],
        interest: ['prayer', 'fellowship']
    },
    'choir-ya': {
        name: 'Sacred Music / Choir',
        description: 'Weekly rehearsal & Mass service',
        details: 'Fill out form: <a href="https://forms.office.com/Pages/ResponsePage.aspx?id=spbPjOu3C0enFewWltg-vSGAojmE4WpCvxL72BS8279UN0RYT042M0dDNlNLQ0ZTSDlFQ1ZWMTdKWC4u" target="_blank">Sacred Music Interest Form</a><br>Or contact <a href="mailto:nrankin@stedward.org">nrankin@stedward.org</a>',
        age: ['college-young-adult'],
        interest: ['music', 'prayer']
    },
    'knights-ya': {
        name: 'Knights of Columbus',
        description: 'Catholic men\'s fraternal organization focused on charity, unity, fraternity, and patriotism',
        details: 'Visit <a href="https://stedward.org/kofc" target="_blank">stedward.org/kofc</a> for more information',
        age: ['college-young-adult'],
        gender: ['male'],
        interest: ['fellowship', 'service', 'prayer']
    },
    'ladies-aux-ya': {
        name: 'Ladies Auxiliary',
        description: 'Prayer, service, fellowship for women',
        details: 'Visit <a href="https://stedward.org/ladies-auxiliary" target="_blank">stedward.org/ladies-auxiliary</a> for information',
        age: ['college-young-adult'],
        gender: ['female'],
        interest: ['fellowship', 'service', 'prayer']
    },
    
    // Spouses and Parents
    'marriage-enrichment': {
        name: 'Marriage Enrichment Nights',
        description: 'Strengthen your marriage through faith',
        details: 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for schedule',
        age: ['married-parents'],
        state: ['married'],
        interest: ['fellowship', 'education', 'support']
    },
    'knights-parents': {
        name: 'Knights of Columbus',
        description: 'Men\'s service fraternity with monthly Cor Nights and insurance benefits',
        details: 'Visit <a href="https://stedward.org/kofc" target="_blank">stedward.org/kofc</a> for information',
        age: ['married-parents'],
        gender: ['male'],
        interest: ['fellowship', 'service']
    },
    'ladies-aux-parents': {
        name: 'Ladies Auxiliary',
        description: 'Service, crafts, Angel-Tree outreach',
        details: 'Visit <a href="https://stedward.org/ladies-auxiliary" target="_blank">stedward.org/ladies-auxiliary</a> for information',
        age: ['married-parents'],
        gender: ['female'],
        interest: ['fellowship', 'service']
    },
    'coffee-donuts-parents': {
        name: 'Coffee-&-Donuts Hospitality Team',
        description: 'Once a month after-Mass fellowship in Little Carrel Room',
        details: 'Visit <a href="https://stedward.org/coffee-donuts" target="_blank">stedward.org/coffee-donuts</a> to volunteer',
        age: ['married-parents'],
        interest: ['fellowship', 'service']
    },
    'bereavement-parents': {
        name: 'Bereavement Meal Ministry',
        description: 'Cook/serve funeral-day luncheons',
        details: 'Visit <a href="https://stedward.org/bereavement" target="_blank">stedward.org/bereavement</a> to participate',
        age: ['married-parents'],
        interest: ['service']
    },
    'svdp-parents': {
        name: 'St. Vincent de Paul Society',
        description: 'Support for neighbors in need - meet first Sunday monthly',
        details: 'Call Rick Prickett (615) 283-0374 or visit <a href="https://stedward.org/st-vincent-de-paul" target="_blank">stedward.org/st-vincent-de-paul</a>',
        age: ['married-parents'],
        interest: ['service']
    },
    
    // Journeying Adults
    'svdp-adults': {
        name: 'St. Vincent de Paul Society',
        description: 'Helping neighbors in need - meet first Sunday monthly in Scout Room',
        details: 'Call Rick Prickett (615) 283-0374 or visit <a href="https://stedward.org/st-vincent-de-paul" target="_blank">stedward.org/st-vincent-de-paul</a>',
        age: ['journeying-adults'],
        interest: ['service']
    },
    'hospitality-ministry': {
        name: 'Hospitality Ministry',
        description: 'Welcome and serve parish community',
        details: 'Visit <a href="https://stedward.org/hospitality-ministry" target="_blank">stedward.org/hospitality-ministry</a> for information',
        age: ['journeying-adults'],
        interest: ['fellowship', 'service']
    },
    'coffee-donuts-adults': {
        name: 'Coffee-&-Donuts',
        description: 'Once a month after-Mass fellowship in Little Carrel Room',
        details: 'Visit <a href="https://stedward.org/coffee-donuts" target="_blank">stedward.org/coffee-donuts</a> to volunteer',
        age: ['journeying-adults'],
        interest: ['fellowship', 'service']
    },
    'bereavement-adults': {
        name: 'Bereavement Meal Ministry',
        description: 'Support families during difficult times by cooking and serving funeral luncheons',
        details: 'Visit <a href="https://stedward.org/bereavement" target="_blank">stedward.org/bereavement</a> to participate',
        age: ['journeying-adults'],
        interest: ['service']
    },
    'adoration-guild': {
        name: 'Adoration Guild',
        description: 'Committed prayer before the Blessed Sacrament',
        details: 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for information',
        age: ['journeying-adults'],
        interest: ['prayer']
    },
    'knights-adults': {
        name: 'Knights of Columbus',
        description: 'Catholic men\'s fraternal organization with insurance and financial planning benefits',
        details: 'Visit <a href="https://stedward.org/kofc" target="_blank">stedward.org/kofc</a> to become a St. Edward Knight',
        age: ['journeying-adults'],
        gender: ['male'],
        interest: ['fellowship', 'service']
    },
    'ladies-aux-adults': {
        name: 'Ladies Auxiliary',
        description: 'Women\'s fellowship and service',
        details: 'Visit <a href="https://stedward.org/ladies-auxiliary" target="_blank">stedward.org/ladies-auxiliary</a> for information',
        age: ['journeying-adults'],
        gender: ['female'],
        interest: ['fellowship', 'service']
    },
    'catechists': {
        name: 'Catechists',
        description: 'Teach faith formation classes',
        details: 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for information',
        age: ['journeying-adults'],
        interest: ['education', 'service']
    },
    'choir-adults': {
        name: 'Sacred Music / Choir',
        description: 'Weekly rehearsal & Mass service',
        details: 'Fill out form: <a href="https://forms.office.com/Pages/ResponsePage.aspx?id=spbPjOu3C0enFewWltg-vSGAojmE4WpCvxL72BS8279UN0RYT042M0dDNlNLQ0ZTSDlFQ1ZWMTdKWC4u" target="_blank">Sacred Music Interest Form</a><br>Or contact <a href="mailto:nrankin@stedward.org">nrankin@stedward.org</a>',
        age: ['journeying-adults'],
        interest: ['music', 'prayer']
    },
    'liturgical-adults': {
        name: 'Serving at Mass',
        description: 'Lector, EMHC, Usher',
        details: 'Visit <a href="https://stedward.org/liturgical" target="_blank">stedward.org/liturgical</a> for training',
        age: ['journeying-adults'],
        interest: ['prayer', 'service']
    },
    'room-inn-adults': {
        name: 'Room In The Inn',
        description: 'Service & hospitality for homeless men during winter months',
        details: 'Visit <a href="https://stedward.org/room-in-the-inn" target="_blank">stedward.org/room-in-the-inn</a> or contact Greg Beem',
        age: ['journeying-adults'],
        interest: ['service']
    },
    'haiti-sister-parish': {
        name: 'Haiti Sister Parish Support',
        description: 'Support our sister parish in Haiti',
        details: 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for information',
        age: ['journeying-adults'],
        interest: ['service']
    },
    'bible-bunco': {
        name: 'Bible Bunco & Blessings',
        description: 'Faith and fellowship through games',
        details: 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for information',
        age: ['journeying-adults'],
        gender: ['female'],
        interest: ['fellowship', 'education']
    },
    
    // Always Available
    'mass': {
        name: 'Daily & Sunday Mass',
        description: 'The source and summit of our faith',
        details: 'Mass times available at <a href="https://stedward.org" target="_blank">stedward.org</a>',
        age: ['infant', 'kid', 'junior-high', 'high-school', 'college-young-adult', 'married-parents', 'journeying-adults'],
        interest: ['prayer', 'all']
    },
    'returning-catholic': {
        name: 'If It\'s Been A While...',
        description: 'Gentle return to the Catholic Church',
        details: 'Call (615) 833-5520 or email <a href="mailto:support@stedward.org">support@stedward.org</a>',
        age: ['college-young-adult', 'married-parents', 'journeying-adults'],
        interest: ['prayer', 'education', 'all'],
        situation: ['returning-to-church']
    },
    'welcome-committee': {
        name: 'Welcome to St. Edward!',
        description: 'New parishioner orientation and support',
        details: 'Register online: <a href="https://stedwardnash.flocknote.com/register" target="_blank">stedwardnash.flocknote.com/register</a><br>Follow us: <a href="https://www.instagram.com/stedwardcommunity/" target="_blank">Instagram</a> | <a href="https://www.facebook.com/stedwardschool" target="_blank">Facebook</a><br>Photo galleries: <a href="https://stedward.smugmug.com/" target="_blank">stedward.smugmug.com</a>',
        age: ['college-young-adult', 'married-parents', 'journeying-adults'],
        interest: ['fellowship', 'all'],
        situation: ['new-to-stedward']
    },
    'nashville-newcomers': {
        name: 'Nashville Newcomers Group',
        description: 'Connect with other families new to Nashville',
        details: 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for information',
        age: ['college-young-adult', 'married-parents', 'journeying-adults'],
        interest: ['fellowship', 'all'],
        situation: ['new-to-nashville']
    }
};
