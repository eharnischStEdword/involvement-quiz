MINISTRY_DATA = {
    # Sacraments
    'mass': {
        'name': 'Come to Mass!',
        'description': 'The source and summit of our faith',
        'details': 'Daily & Sunday Mass times are available at <a href="https://stedward.org" target="_blank">stedward.org</a>.',
        'age': ['infant', 'elementary', 'junior-high', 'high-school', 'college-young-adult', 'married-parents', 'journeying-adults'],
        'interest': ['prayer', 'all']
    },
    'confession': {
        'name': 'Sacrament of Confession',
        'description': 'Reconciliation and spiritual healing',
        'details': 'Confession times available at <a href="https://stedward.org" target="_blank">stedward.org</a>',
        'age': ['elementary', 'junior-high', 'high-school', 'college-young-adult', 'married-parents', 'journeying-adults'],
        'interest': ['prayer', 'all']
    },
    'ocia': {
        'name': 'OCIA (Adult Baptism/Full Communion)',
        'description': 'Program that prepares adults for Baptism, Holy Communion & Confirmation',
        'details': 'Visit <a href="https://stedward.org/ocia" target="_blank">stedward.org/ocia</a> for more information',
        'age': ['college-young-adult', 'married-parents', 'journeying-adults'],
        'interest': ['education', 'prayer']
    },
    'infant-baptism': {
        'name': 'Baptism',
        'description': "We're looking forward to your children receiving the grace of Baptism!",
        'details': 'To start with Baptism preparation for families with young children, visit <a href="https://stedward.org/baptism" target="_blank">stedward.org/baptism</a>',
        'age': ['infant', 'married-parents', 'journeying-adults'],
        'state': ['parent'],
        'interest': ['education', 'prayer', 'kids', 'all']
    },
    'marriage-convalidation': {
        'name': 'Marriage Convalidation',
        'description': 'Sacrament of Holy Matrimony for civilly married couples',
        'details': 'Fill out intake form at <a href="https://stedward.org/marriage-prep" target="_blank">stedward.org/marriage-prep</a>',
        'age': ['college-young-adult', 'married-parents'],
        'state': ['married'],
        'interest': ['education', 'prayer']
    },
    
    # Welcome & New Member Support
    'welcome-committee': {
        'name': 'Welcome to St. Edward!',
        'description': 'New parishioner orientation and support',
        'details': 'Register online: <a href="https://stedwardnash.flocknote.com/register" target="_blank">stedwardnash.flocknote.com/register</a><br>Follow us: <a href="https://www.instagram.com/stedwardcommunity/" target="_blank">Instagram</a> | <a href="https://www.facebook.com/stedwardschool" target="_blank">Facebook</a><br>Photo galleries: <a href="https://stedward.smugmug.com/" target="_blank">stedward.smugmug.com</a>',
        'age': ['college-young-adult', 'married-parents', 'journeying-adults'],
        'interest': ['fellowship', 'all'],
        'situation': ['new-to-stedward']
    },
    'returning-catholic': {
        'name': "If It's Been A While...",
        'description': "Welcome! We're happy you're here!",
        'details': 'Call (615) 833-5520 or <a href="https://stedward.org/contact-us" target="_blank">contact the Church Office</a>',
        'age': ['college-young-adult', 'married-parents', 'journeying-adults'],
        'interest': ['prayer', 'education', 'all'],
        'situation': ['returning-to-church']
    },
    
    # Knights of Columbus (by age group)
    'knights-ya': {
        'name': 'Knights of Columbus',
        'description': "Catholic men's fraternal organization - Focus on charity, unity, fraternity, and patriotism",
        'details': 'Visit <a href="https://stedward.org/kofc" target="_blank">stedward.org/kofc</a> for more information',
        'age': ['college-young-adult'],
        'gender': ['male'],
        'interest': ['fellowship', 'service', 'prayer']
    },
    'knights-parents': {
        'name': 'Knights of Columbus',
        'description': "Catholic men's fraternal organization - Service fraternity with monthly Cor Nights and insurance benefits",
        'details': 'Visit <a href="https://stedward.org/kofc" target="_blank">stedward.org/kofc</a> for more information',
        'age': ['married-parents'],
        'gender': ['male'],
        'interest': ['fellowship', 'service']
    },
    'knights-adults': {
        'name': 'Knights of Columbus',
        'description': "Catholic men's fraternal organization - Full benefits including insurance and financial planning",
        'details': 'Visit <a href="https://stedward.org/kofc" target="_blank">stedward.org/kofc</a> to become a St. Edward Knight',
        'age': ['journeying-adults'],
        'gender': ['male'],
        'interest': ['fellowship', 'service']
    },
    
    # Ladies Auxiliary (by age group)
    'ladies-aux-ya': {
        'name': 'Ladies Auxiliary',
        'description': "Women's fellowship and service - Prayer, service, fellowship for women",
        'details': 'Visit <a href="https://stedward.org/ladies-auxiliary" target="_blank">stedward.org/ladies-auxiliary</a> for information',
        'age': ['college-young-adult'],
        'gender': ['female'],
        'interest': ['fellowship', 'service', 'prayer']
    },
    'ladies-aux-parents': {
        'name': 'Ladies Auxiliary',
        'description': "Women's fellowship and service - Service, crafts, Angel-Tree outreach",
        'details': 'Visit <a href="https://stedward.org/ladies-auxiliary" target="_blank">stedward.org/ladies-auxiliary</a> for information',
        'age': ['married-parents'],
        'gender': ['female'],
        'interest': ['fellowship', 'service']
    },
    'ladies-aux-adults': {
        'name': 'Ladies Auxiliary',
        'description': "Women's fellowship and service",
        'details': 'Visit <a href="https://stedward.org/ladies-auxiliary" target="_blank">stedward.org/ladies-auxiliary</a> for information',
        'age': ['journeying-adults'],
        'gender': ['female'],
        'interest': ['fellowship', 'service']
    },
    
    # Sacred Music/Choir (by age group)
    'choir-hs': {
        'name': 'Sacred Music / Choir',
        'description': 'Weekly rehearsal & Mass service (Age 16+)',
        'details': 'Fill out form: <a href="https://forms.office.com/Pages/ResponsePage.aspx?id=spbPjOu3C0enFewWltg-vSGAojmE4WpCvxL72BS8279UN0RYT042M0dDNlNLQ0ZTSDlFQ1ZWMTdKWC4u" target="_blank">Sacred Music Interest Form</a><br>Or contact <a href="mailto:nrankin@stedward.org">nrankin@stedward.org</a>',
        'age': ['high-school'],
        'interest': ['music', 'prayer']
    },
    'choir-ya': {
        'name': 'Sacred Music / Choir',
        'description': 'Weekly rehearsal & Mass service',
        'details': 'Fill out form: <a href="https://forms.office.com/Pages/ResponsePage.aspx?id=spbPjOu3C0enFewWltg-vSGAojmE4WpCvxL72BS8279UN0RYT042M0dDNlNLQ0ZTSDlFQ1ZWMTdKWC4u" target="_blank">Sacred Music Interest Form</a><br>Or contact <a href="mailto:nrankin@stedward.org">nrankin@stedward.org</a>',
        'age': ['college-young-adult'],
        'interest': ['music', 'prayer']
    },
    'choir-adults': {
        'name': 'Sacred Music / Choir',
        'description': 'Weekly rehearsal & Mass service',
        'details': 'Fill out form: <a href="https://forms.office.com/Pages/ResponsePage.aspx?id=spbPjOu3C0enFewWltg-vSGAojmE4WpCvxL72BS8279UN0RYT042M0dDNlNLQ0ZTSDlFQ1ZWMTdKWC4u" target="_blank">Sacred Music Interest Form</a><br>Or contact <a href="mailto:nrankin@stedward.org">nrankin@stedward.org</a>',
        'age': ['journeying-adults'],
        'interest': ['music', 'prayer']
    },
    
    # Fraternus (by age group)
    'fraternus-jr': {
        'name': 'Fraternus',
        'description': 'Brotherhood & virtue formation - Weekly meetings and excursions developing Catholic men',
        'details': 'Wednesdays 6:00-8:00pm. <a href="https://stedward.org/contact-us" target="_blank">Contact the Church Office</a> for information',
        'age': ['junior-high'],
        'gender': ['male'],
        'interest': ['fellowship', 'education']
    },
    'fraternus-hs': {
        'name': 'Fraternus',
        'description': 'Brotherhood & virtue formation - Weekly formation, excursions, and retreats developing virtuous Catholic men',
        'details': 'Wednesdays 6:00-8:00pm with 4 weekend excursions. <a href="https://stedward.org/contact-us" target="_blank">Contact the Church Office</a> for information',
        'age': ['high-school'],
        'gender': ['male'],
        'interest': ['fellowship', 'education']
    },
    'fraternus-mentors': {
        'name': 'Fraternus Adult Mentors',
        'description': 'College men serve younger boys (Wednesday evenings)',
        'details': '<a href="https://stedward.org/contact-us" target="_blank">Contact the Church Office</a> for information',
        'age': ['college-young-adult'],
        'gender': ['male'],
        'interest': ['service', 'fellowship']
    },
    
    # Fidelis (by age group)
    'fidelis-hs': {
        'name': 'Fidelis',
        'description': 'Sisterhood & virtue formation - Faith-filled friendships through discussion, activities, and fun',
        'details': 'Bi-weekly Wednesdays 6:30-8:30pm. Contact <a href="mailto:fidelisnashville@gmail.com">fidelisnashville@gmail.com</a>',
        'age': ['junior-high', 'high-school'],
        'gender': ['female'],
        'interest': ['fellowship', 'education']
    },
    
    # Totus Tuus (corrected)
    'totus-tuus-kids': {
        'name': 'Totus Tuus Summer Program (Grades 1-6)',
        'description': 'Week-long summer catechetical program with games, activities, and faith formation',
        'details': 'Similar to Vacation Bible School with college-age teachers. The week is filled with faith, fun, and friendship through engaging activities based on Sacred Scripture and the Catechism.<br><br>Visit <a href="https://stedward.org/totus-tuus" target="_blank">stedward.org/totus-tuus</a> - registration opens in spring',
        'age': ['elementary'],
        'interest': ['education', 'fellowship', 'prayer', 'kids']
    },
    'totus-tuus-teens': {
        'name': 'Totus Tuus Summer Program (Grades 7-12)',
        'description': 'Week-long summer catechetical program for teens with faith formation and fellowship',
        'details': 'College-age missionaries provide catechetical instruction based on Sacred Scripture and the Catechism. The week is filled with faith, fun, and friendship through engaging activities.<br><br>Visit <a href="https://stedward.org/totus-tuus" target="_blank">stedward.org/totus-tuus</a> - registration opens in spring',
        'age': ['junior-high', 'high-school'],
        'interest': ['education', 'fellowship', 'prayer']
    },
    
    # PREP (consolidated)
    'prep-kids': {
        'name': 'PREP - Sunday Religious Ed',
        'description': 'Faith formation including First Confession & First Holy Communion prep, and sacrament preparation for all ages',
        'details': 'Visit <a href="https://stedward.org/prep" target="_blank">stedward.org/prep</a> to register',
        'age': ['elementary', 'junior-high'],
        'interest': ['education', 'prayer', 'kids']
    },
    
    # Coffee & Donuts (by age group)
    'coffee-donuts-parents': {
        'name': 'Coffee & Donuts Hospitality Team',
        'description': 'Once a month after-Mass fellowship in Little Carrel Room - Grab a treat for the ride home!',
        'details': 'Just stop on by! Interested in helping out? Visit <a href="https://stedward.org/coffee-donuts" target="_blank">stedward.org/coffee-donuts</a> to volunteer',
        'age': ['married-parents'],
        'interest': ['fellowship', 'service']
    },
    'coffee-donuts-adults': {
        'name': 'Coffee & Donuts Hospitality Team',
        'description': 'Once a month after-Mass fellowship in Little Carrel Room',
        'details': 'Just stop on by! Interested in helping out? Visit <a href="https://stedward.org/coffee-donuts" target="_blank">stedward.org/coffee-donuts</a> to volunteer',
        'age': ['journeying-adults'],
        'interest': ['fellowship', 'service']
    },
    
    # Bereavement Ministry (by age group)
    'bereavement-parents': {
        'name': 'Bereavement Meal Ministry',
        'description': 'Support families - Cook/serve funeral-day luncheons',
        'details': 'Visit <a href="https://stedward.org/bereavement" target="_blank">stedward.org/bereavement</a> to find out more',
        'age': ['married-parents'],
        'interest': ['service']
    },
    'bereavement-adults': {
        'name': 'Bereavement Meal Ministry',
        'description': 'Support families during difficult times by cooking and serving funeral luncheons',
        'details': 'Visit <a href="https://stedward.org/bereavement" target="_blank">stedward.org/bereavement</a> to find out more',
        'age': ['journeying-adults'],
        'interest': ['service']
    },
    
    # St. Vincent de Paul (by age group)
    'svdp-parents': {
        'name': 'St. Vincent de Paul Society',
        'description': 'Helping neighbors in need - Support for neighbors in need, meet first Sunday monthly',
        'details': 'Call Rick Prickett (615) 283-0374 or visit <a href="https://stedward.org/st-vincent-de-paul" target="_blank">stedward.org/st-vincent-de-paul</a>',
        'age': ['married-parents'],
        'interest': ['service']
    },
    'svdp-adults': {
        'name': 'St. Vincent de Paul Society',
        'description': 'Helping neighbors in need - Meet first Sunday monthly in Scout Room',
        'details': 'Call Rick Prickett (615) 283-0374 or visit <a href="https://stedward.org/st-vincent-de-paul" target="_blank">stedward.org/st-vincent-de-paul</a>',
        'age': ['journeying-adults'],
        'interest': ['service']
    },
    
    # Parent Support
    'moms-group': {
        'name': 'Moms Group',
        'description': 'Spiritual & practical support for mothers with rosary walks and monthly brunch',
        'details': 'Join on Flocknote: <a href="https://stedwardnash.flocknote.com/signup/180620" target="_blank">stedwardnash.flocknote.com/signup/180620</a><br>Or join GroupMe: <a href="https://groupme.com/join_group/107457911/mdAevstX" target="_blank">groupme.com/join_group/107457911/mdAevstX</a>',
        'age': ['infant', 'married-parents'],
        'gender': ['female'],
        'state': ['parent'],
        'interest': ['fellowship', 'support', 'prayer']
    },
    'meal-train-receive': {
        'name': 'Meal Train Support for Your Family',
        'description': 'We want to serve you and support you with our meal train for families with new members!',
        'details': 'Contact <a href="mailto:elizabethlansden@gmail.com">elizabethlansden@gmail.com</a> if your family is growing soon and would like to receive meals',
        'age': ['infant'],
        'interest': ['support', 'fellowship', 'all']
    },
    'meal-train-provide': {
        'name': 'Meal Train for New Families',
        'description': 'Support growing families with meal delivery when they welcome a baby, adopt, or receive a foster child',
        'details': 'Flexible commitment - participate 1-3 times per year. Contact <a href="mailto:elizabethlansden@gmail.com">elizabethlansden@gmail.com</a> to join the volunteer list',
        'age': ['married-parents', 'college-young-adult', 'journeying-adults'],
        'interest': ['service', 'fellowship', 'support']
    },
    
    # Kids Programs
    'st-edward-school': {
        'name': 'St. Edward School (PreK-8th Grade)',
        'description': 'Catholic education in a faith-filled community environment',
        'details': 'Apply for enrollment: <a href="https://ses.stedward.org/apply" target="_blank">ses.stedward.org/apply</a>',
        'age': ['elementary'],
        'interest': ['education', 'fellowship', 'all']
    },
    'cub-scouts': {
        'name': 'Cub Scouts',
        'description': 'Character development and outdoor adventures for boys and girls',
        'details': 'Visit <a href="https://stedward.org/scouting" target="_blank">stedward.org/scouting</a> for more information and contact details',
        'age': ['elementary'],
        'interest': ['fellowship', 'service', 'all']
    },
    'catechesis': {
        'name': 'Catechesis of the Good Shepherd Atrium',
        'description': 'Montessori-based religious education for Pre-K-2',
        'details': '<a href="https://stedward.org/contact-us" target="_blank">Contact the Church Office</a> for enrollment',
        'age': ['elementary'],
        'interest': ['education', 'prayer']
    },
    
    # High School Liturgical
    'liturgical-hs': {
        'name': 'Liturgical Ministries (Age 16+)',
        'description': 'Serve as lector, hospitality, or EMHC',
        'details': '<a href="https://stedward.org/lectors" target="_blank">Lector Ministry</a> • <a href="https://stedward.org/hospitality-ministry" target="_blank">Hospitality Ministry</a> • <a href="https://stedward.org/eucharistic-ministers" target="_blank">EMHC Ministry</a><br><br><a href="https://stedward.org/contact-us" target="_blank">Contact the Church Office to learn more</a>',
        'age': ['high-school'],
        'interest': ['service', 'prayer']
    },
    
    # Young Adult Programs
    'theology-tap': {
        'name': 'Theology on Tap (Summer Series)',
        'description': 'Faith & fellowship in beer-garden setting with engaging speakers',
        'details': 'Visit <a href="https://stedward.org/theo-on-tap" target="_blank">stedward.org/theo-on-tap</a> - check bulletin for dates',
        'age': ['college-young-adult'],
        'interest': ['fellowship', 'education']
    },
    'ocia-sponsors': {
        'name': 'OCIA Sponsors',
        'description': 'Accompany adults entering the Church',
        'details': '<a href="https://stedward.org/contact-us" target="_blank">Contact the Church Office</a> for information',
        'age': ['college-young-adult'],
        'interest': ['service', 'education']
    },
    'room-inn-ya': {
        'name': 'Room-in-the-Inn Shelter Crew',
        'description': 'Saturday-night hospitality for homeless men during winter months',
        'details': '<a href="https://stedward.org/contact-us" target="_blank">Contact the Church Office</a> for information about Greg Beem',
        'age': ['college-young-adult'],
        'interest': ['service']
    },
    'cursillo': {
        'name': 'Cursillo Retreats',
        'description': 'Three-day renewal weekends focused on spiritual growth',
        'details': 'Visit <a href="https://stedward.org/cursillo" target="_blank">stedward.org/cursillo</a> for information',
        'age': ['college-young-adult'],
        'interest': ['prayer', 'fellowship']
    },
    
    # Marriage & Family
    'marriage-enrichment': {
        'name': 'Marriage Enrichment Nights',
        'description': 'Strengthen your marriage through faith',
        'details': '<a href="https://stedward.org/contact-us" target="_blank">Contact the Church Office</a> for schedule',
        'age': ['married-parents'],
        'state': ['married'],
        'interest': ['fellowship', 'education', 'support']
    },
    
    # Adult Ministries
    'hospitality-ministry': {
        'name': 'Hospitality Ministry',
        'description': 'Welcome and serve parish community',
        'details': 'Visit <a href="https://stedward.org/hospitality-ministry" target="_blank">stedward.org/hospitality-ministry</a> for information',
        'age': ['journeying-adults'],
        'interest': ['fellowship', 'service']
    },
    'adoration-guild': {
        'name': 'Adoration Guild',
        'description': 'Committed prayer before the Blessed Sacrament',
        'details': '<a href="https://stedward.org/contact-us" target="_blank">Contact the Church Office</a> for information',
        'age': ['journeying-adults'],
        'interest': ['prayer']
    },
    'catechists': {
        'name': 'Catechists',
        'description': 'Teach faith formation classes',
        'details': '<a href="https://stedward.org/contact-us" target="_blank">Contact the Church Office</a> for information',
        'age': ['journeying-adults'],
        'interest': ['education', 'service']
    },
    'liturgical-adults': {
        'name': 'Serving at Mass',
        'description': 'Lector, EMHC, Usher',
        'details': '<a href="https://stedward.org/lectors" target="_blank">Lector Ministry</a> • <a href="https://stedward.org/hospitality-ministry" target="_blank">Hospitality Ministry</a> • <a href="https://stedward.org/eucharistic-ministers" target="_blank">EMHC Ministry</a><br><br><a href="https://stedward.org/contact-us" target="_blank">Contact the Church Office to learn more</a>',
        'age': ['journeying-adults'],
        'interest': ['prayer', 'service']
    },
    'room-inn-adults': {
        'name': 'Room In The Inn',
        'description': 'Service & hospitality for homeless men during winter months',
        'details': 'Visit <a href="https://stedward.org/room-in-the-inn" target="_blank">stedward.org/room-in-the-inn</a> or <a href="https://stedward.org/contact-us" target="_blank">contact the Church Office</a> for Greg Beem',
        'age': ['journeying-adults'],
        'interest': ['service']
    },
    'haiti-sister-parish': {
        'name': 'Haiti Sister Parish Support',
        'description': 'Support our sister parish in Haiti',
        'details': '<a href="https://stedward.org/contact-us" target="_blank">Contact the Church Office</a> for information',
        'age': ['journeying-adults'],
        'interest': ['service']
    },
    'bible-bunco': {
        'name': 'Bible Bunco & Blessings',
        'description': 'Faith and fellowship through games',
        'details': '<a href="https://stedward.org/contact-us" target="_blank">Contact the Church Office</a> for information',
        'age': ['journeying-adults'],
        'gender': ['female'],
        'interest': ['fellowship', 'education']
    }
}
