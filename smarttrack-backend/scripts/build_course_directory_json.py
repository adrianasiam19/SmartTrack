"""One-shot builder for data/course_directory.json (run from smarttrack-backend)."""
from __future__ import annotations

import json
from pathlib import Path

FIELDS_ORDER = [
    "Health Sciences",
    "Engineering",
    "Computer & IT",
    "Business & Economics",
    "Natural Sciences",
    "Agriculture & Environment",
    "Built Environment",
    "Education",
    "Social Sciences & Arts",
    "Creative Arts & Communication",
    "Law",
]

# slug, name, field, brief, topics(;), careers(;), shs(;), unis(;), detail
RAW: list[tuple[str, str, str, str, str, str, str, str, str]] = []

def add(*row: str) -> None:
    RAW.append(tuple(row))  # type: ignore[arg-type]


# Health
add("medicine-mbchb", "MBChB Medicine", "Health Sciences",
    "Train as a medical doctor with clinical rotations and biomedical science foundations.",
    "Anatomy; Physiology; Pathology; Pharmacology; Clinical medicine; Community health",
    "Medical doctor; Clinical researcher; Public health physician",
    "Biology; Chemistry; Physics; Elective Mathematics",
    "University of Ghana; KNUST; UCC; UDS",
    "Medicine combines biomedical science with supervised clinical practice. Students study the structure and function of the human body, disease processes, and patient care across hospital and community settings. Graduates typically complete internship and residency pathways before independent practice.")
add("nursing", "BSc Nursing", "Health Sciences",
    "Prepare for professional nursing with patient care, clinical skills, and health promotion.",
    "Fundamentals of nursing; Medical-surgical nursing; Maternal health; Community nursing; Pharmacology",
    "Registered nurse; Midwifery pathway; Public health nurse; Nurse educator",
    "Biology; Chemistry; English; Social Studies",
    "University of Ghana; KNUST; UCC; UEW; UDS",
    "Nursing programmes develop clinical judgment, compassionate care, and evidence-based practice through ward and community placements.")
add("pharmacy", "Doctor of Pharmacy / BPharm", "Health Sciences",
    "Study medicines, patient counselling, and pharmaceutical science for community or hospital pharmacy.",
    "Pharmaceutical chemistry; Pharmacology; Pharmaceutics; Clinical pharmacy; Pharmacy practice",
    "Pharmacist; Clinical pharmacist; Regulatory affairs; Pharmaceutical industry",
    "Biology; Chemistry; Physics; Elective Mathematics",
    "KNUST; University of Ghana; UCC",
    "Pharmacy education covers how medicines are designed, dispensed, and used safely across hospitals, community pharmacies, industry, and regulation.")
add("medical-laboratory-science", "BSc Medical Laboratory Science", "Health Sciences",
    "Learn diagnostic laboratory techniques used to detect and monitor disease.",
    "Haematology; Microbiology; Clinical chemistry; Immunology; Lab management",
    "Medical laboratory scientist; Diagnostic specialist; Research technician",
    "Biology; Chemistry; Physics",
    "KNUST; University of Ghana; UCC; UDS",
    "Students learn to analyse blood, tissues, and other specimens that guide clinical decisions, with strong emphasis on biosafety and quality control.")
add("physician-assistantship", "BSc Physician Assistantship", "Health Sciences",
    "Train to support physicians in diagnosis, treatment, and primary care delivery.",
    "Clinical medicine; Physical diagnosis; Emergency care; Pharmacology; Community practice",
    "Physician assistant; Primary care clinician; Emergency support clinician",
    "Biology; Chemistry; Physics",
    "KNUST; University of Cape Coast",
    "Physician assistant programmes blend medical science with practical clinical training under physician supervision.")
add("physiotherapy", "BSc Physiotherapy and Sports Science", "Health Sciences",
    "Restore movement and function through rehabilitation science and therapeutic exercise.",
    "Anatomy; Biomechanics; Therapeutic exercise; Sports injuries; Rehabilitation",
    "Physiotherapist; Sports therapist; Rehabilitation specialist",
    "Biology; Physics; Chemistry",
    "KNUST; University of Ghana",
    "Students study how the body moves and recovers, then apply exercise and education to help patients regain function.")
add("midwifery", "BSc Midwifery", "Health Sciences",
    "Specialise in pregnancy, childbirth, and newborn care in clinical and community settings.",
    "Antenatal care; Labour and delivery; Postnatal care; Neonatal health; Reproductive health",
    "Midwife; Maternal health specialist; Community midwife",
    "Biology; Chemistry; English",
    "UCC; University of Ghana; KNUST; UDS",
    "Midwifery focuses on safe motherhood and newborn wellbeing, including emergency obstetric skills and family health education.")
add("dental-surgery", "BSc Dental Surgery", "Health Sciences",
    "Study oral health, dental procedures, and preventive dentistry.",
    "Oral anatomy; Restorative dentistry; Oral surgery basics; Preventive dentistry; Radiology",
    "Dentist; Oral health clinician; Dental public health",
    "Biology; Chemistry; Physics",
    "University of Ghana; KNUST",
    "Dental programmes combine biomedical science with clinical dentistry to diagnose and treat oral disease.")
add("veterinary-medicine", "DVM Veterinary Medicine", "Health Sciences",
    "Care for animal health across companion, livestock, and public-health contexts.",
    "Animal anatomy; Pathology; Surgery; Livestock health; Zoonoses",
    "Veterinarian; Livestock health officer; Veterinary public health",
    "Biology; Chemistry; Physics",
    "KNUST; University of Ghana",
    "Veterinary medicine covers animal care plus disease control that protects both animal and human health.")
add("public-health", "BSc Public Health", "Health Sciences",
    "Prevent disease and improve population health through epidemiology and health systems.",
    "Epidemiology; Biostatistics; Health promotion; Environmental health; Health policy",
    "Public health officer; NGO health programme officer; Health educator",
    "Biology; Social Studies; English; Elective Mathematics",
    "University of Ghana; KNUST; UCC; UDS",
    "Public health looks beyond individual patients to communities and systems that reduce disease burden.")
add("nutrition-dietetics", "BSc Nutrition and Dietetics", "Health Sciences",
    "Apply food science and clinical nutrition to promote health and manage disease.",
    "Human nutrition; Diet therapy; Food science; Community nutrition; Biochemistry",
    "Dietitian; Nutritionist; Food service manager; Public health nutritionist",
    "Biology; Chemistry; Home Economics",
    "University of Ghana; KNUST; UCC",
    "Students learn how nutrients affect the body and how tailored diets support wellness and recovery.")
add("medical-imaging", "BSc Medical Imaging", "Health Sciences",
    "Produce and interpret medical images that support diagnosis and treatment.",
    "Radiographic technique; Anatomy; Radiation protection; Ultrasound basics; Image evaluation",
    "Radiographer; Medical imaging technologist",
    "Biology; Physics; Chemistry; Mathematics",
    "University of Ghana; KNUST",
    "Medical imaging trains students to operate equipment safely and produce diagnostic-quality images.")
add("herbal-medicine", "BSc Herbal Medicine", "Health Sciences",
    "Study medicinal plants and integrative approaches within a scientific framework.",
    "Pharmacognosy; Phytochemistry; Traditional medicine; Clinical herbal practice",
    "Herbal medicine practitioner; Phytotherapy researcher",
    "Biology; Chemistry",
    "KNUST",
    "This programme connects ethnobotany and laboratory science for responsible plant-based therapies.")
add("optometry", "BSc Optometry", "Health Sciences",
    "Examine eyes, prescribe corrective lenses, and manage common visual disorders.",
    "Ocular anatomy; Optics; Refraction; Contact lenses; Clinical optometry",
    "Optometrist; Vision care clinician",
    "Biology; Physics; Chemistry; Mathematics",
    "KNUST",
    "Optometry blends optics with clinical eye care for vision assessment and ocular health.")

# Engineering
add("computer-engineering", "BSc Computer Engineering", "Engineering",
    "Design computing hardware and embedded systems at the intersection of EE and CS.",
    "Digital systems; Microprocessors; Embedded systems; Computer networks; Electronics",
    "Computer engineer; Embedded systems engineer; Hardware engineer",
    "Elective Mathematics; Physics; Chemistry; ICT",
    "KNUST; University of Ghana; UMaT",
    "Computer engineering focuses on how hardware and low-level software work together in modern devices.")
add("electrical-engineering", "BSc Electrical Engineering", "Engineering",
    "Design and analyse electrical power, electronics, and control systems.",
    "Circuit theory; Power systems; Electronics; Control systems; Machines",
    "Electrical engineer; Power systems engineer; Electronics engineer",
    "Elective Mathematics; Physics; Chemistry",
    "KNUST; University of Ghana; UMaT; TTU",
    "Students learn to generate, distribute, and use electrical energy across industry and infrastructure.")
add("civil-engineering", "BSc Civil Engineering", "Engineering",
    "Plan and build infrastructure such as roads, bridges, water systems, and structures.",
    "Structural analysis; Geotechnics; Hydraulics; Transportation; Construction management",
    "Civil engineer; Structural engineer; Project engineer",
    "Elective Mathematics; Physics; Chemistry",
    "KNUST; University of Ghana; UMaT; CKT-UTAS",
    "Civil engineering trains graduates to design resilient infrastructure for communities.")
add("mechanical-engineering", "BSc Mechanical Engineering", "Engineering",
    "Design machines, thermal systems, and manufacturing processes.",
    "Thermodynamics; Mechanics; Manufacturing; Machine design; Fluid mechanics",
    "Mechanical engineer; Manufacturing engineer; Maintenance engineer",
    "Elective Mathematics; Physics; Chemistry",
    "KNUST; University of Ghana; UMaT; TTU",
    "Mechanical engineers apply physics and design methods to engines, plants, tools, and production lines.")
add("chemical-engineering", "BSc Chemical Engineering", "Engineering",
    "Turn raw materials into useful products through chemical process design.",
    "Process engineering; Reaction engineering; Thermodynamics; Transport phenomena",
    "Chemical engineer; Process engineer; Petrochemical engineer",
    "Elective Mathematics; Chemistry; Physics",
    "KNUST; University of Ghana",
    "Chemical engineering connects chemistry with large-scale process design for fuels, foods, and materials.")
add("biomedical-engineering", "BSc Biomedical Engineering", "Engineering",
    "Apply engineering to medical devices, diagnostics, and healthcare technology.",
    "Biomechanics; Medical instrumentation; Biomaterials; Physiology for engineers",
    "Biomedical engineer; Medical device specialist; Clinical engineer",
    "Elective Mathematics; Physics; Biology; Chemistry",
    "KNUST; University of Ghana",
    "Biomedical engineering sits between medicine and engineering, focusing on devices that diagnose or treat patients.")
add("aerospace-engineering", "BSc Aerospace Engineering", "Engineering",
    "Study aircraft and related aerospace systems, aerodynamics, and propulsion.",
    "Aerodynamics; Flight mechanics; Propulsion; Structures; Avionics basics",
    "Aerospace engineer; Aviation systems engineer",
    "Elective Mathematics; Physics; Chemistry",
    "KNUST",
    "Aerospace programmes emphasise fluid mechanics, structures, and systems engineering for flight technologies.")
add("petroleum-engineering", "BSc Petroleum Engineering", "Engineering",
    "Explore oil and gas exploration, drilling, and production engineering.",
    "Reservoir engineering; Drilling; Production; Petroleum geology basics",
    "Petroleum engineer; Reservoir engineer; Energy operations engineer",
    "Elective Mathematics; Physics; Chemistry",
    "KNUST; UMaT",
    "Students learn how hydrocarbons are located and produced with attention to safety and efficiency.")
add("telecommunications-engineering", "BSc Telecommunication Engineering", "Engineering",
    "Design communication networks, wireless systems, and signal transmission.",
    "Signals and systems; RF communications; Networks; Digital communications",
    "Telecom engineer; Network engineer; RF engineer",
    "Elective Mathematics; Physics; ICT",
    "KNUST; University of Ghana",
    "Telecom engineering covers how voice, data, and media move across wired and wireless networks.")
add("materials-engineering", "BSc Materials Engineering", "Engineering",
    "Study metals, polymers, ceramics, and materials processing for industry.",
    "Materials science; Metallurgy; Polymers; Characterisation; Processing",
    "Materials engineer; Metallurgist; Quality engineer",
    "Elective Mathematics; Physics; Chemistry",
    "KNUST; UMaT",
    "Materials engineers select and improve materials so products are stronger, lighter, or more sustainable.")
add("geological-engineering", "BSc Geological Engineering", "Engineering",
    "Apply geology to engineering problems in mining, construction, and resources.",
    "Engineering geology; Rock mechanics; Hydrogeology; Exploration",
    "Geological engineer; Mining support engineer; Geotechnical specialist",
    "Elective Mathematics; Physics; Chemistry; Geography",
    "KNUST; UMaT",
    "This field connects earth science with engineering design for tunnels, foundations, and mining.")
add("industrial-engineering", "BSc Industrial Engineering", "Engineering",
    "Optimise people, processes, and systems for productivity and quality.",
    "Operations research; Manufacturing systems; Quality control; Ergonomics; Supply chains",
    "Industrial engineer; Process improvement analyst; Operations manager",
    "Elective Mathematics; Physics; Economics",
    "KNUST; University of Ghana",
    "Industrial engineering focuses on efficiency — designing workflows and improving organisational performance.")
add("marine-engineering", "BSc Marine Engineering", "Engineering",
    "Engineering systems for ships and marine operations.",
    "Marine power plants; Naval architecture basics; Marine systems; Maintenance",
    "Marine engineer; Ship systems engineer",
    "Elective Mathematics; Physics; Chemistry",
    "Regional Maritime University",
    "Marine engineering prepares graduates for propulsion and mechanical systems that keep vessels operating safely.")
add("automobile-engineering", "BSc Automobile Engineering", "Engineering",
    "Design, diagnose, and improve automotive systems and vehicle technology.",
    "Vehicle dynamics; Powertrain; Auto electronics; Maintenance technology",
    "Automotive engineer; Vehicle diagnostic specialist",
    "Elective Mathematics; Physics; Chemistry",
    "KNUST; TTU",
    "Automobile programmes blend mechanical and electrical systems for modern vehicles.")

# Computer & IT
add("computer-science", "BSc Computer Science", "Computer & IT",
    "Study algorithms, software development, and computing theory for modern applications.",
    "Programming; Data structures; Databases; Operating systems; Software engineering; AI basics",
    "Software developer; Systems analyst; Data engineer; Research assistant",
    "Elective Mathematics; ICT; Physics",
    "KNUST; University of Ghana; UCC; Ashesi University",
    "Computer Science builds problem-solving skills through coding, theory, and systems design for digital solutions.")
add("information-technology", "BSc Information Technology", "Computer & IT",
    "Apply computing to organisational systems, networks, and user-focused IT services.",
    "Networks; Databases; Web systems; IT project management; Cybersecurity basics",
    "IT specialist; Systems administrator; Business IT analyst",
    "ICT; Elective Mathematics; English",
    "University of Ghana; KNUST; UCC",
    "IT programmes emphasise practical systems organisations rely on — networks, databases, and digital services.")
add("information-systems", "BSc Information Systems", "Computer & IT",
    "Bridge business needs and technology through systems analysis and data management.",
    "Systems analysis; Databases; Business processes; ERP concepts; Data analytics basics",
    "Business analyst; IS analyst; IT consultant",
    "ICT; Elective Mathematics; Economics; Accounting",
    "University of Ghana; KNUST; UCC",
    "Information Systems focuses on how organisations use technology to make decisions and run operations.")
add("cybersecurity", "BSc Cyber Security", "Computer & IT",
    "Protect systems and data through security engineering, risk, and ethical hacking foundations.",
    "Network security; Cryptography basics; Ethical hacking; Risk management; Digital forensics intro",
    "Security analyst; SOC analyst; Security consultant",
    "ICT; Elective Mathematics; Physics",
    "University of Ghana; KNUST",
    "Cybersecurity trains students to identify threats, harden systems, and respond to incidents.")
add("data-science", "BSc Data Science", "Computer & IT",
    "Turn data into insight using statistics, programming, and machine learning foundations.",
    "Statistics; Python/R; Data wrangling; Visualisation; ML intro",
    "Data analyst; Junior data scientist; Business intelligence analyst",
    "Elective Mathematics; ICT; Economics",
    "University of Ghana; KNUST; Ashesi University",
    "Data science combines maths and computing to clean, analyse, and communicate patterns from datasets.")
add("software-engineering", "BSc Software Engineering", "Computer & IT",
    "Engineer reliable software with design patterns, testing, and team development practices.",
    "Software design; Testing; Agile methods; Requirements; Architecture",
    "Software engineer; QA engineer; Product engineer",
    "Elective Mathematics; ICT",
    "KNUST; University of Ghana; Ashesi University",
    "Software engineering emphasises maintainable products — process, quality, and collaboration as well as coding.")
add("computer-networking", "BSc Computer Networking", "Computer & IT",
    "Design and manage computer networks and internet infrastructure.",
    "Routing and switching; Network protocols; Wireless; Network security",
    "Network engineer; Infrastructure specialist",
    "ICT; Elective Mathematics; Physics",
    "KNUST; University of Ghana",
    "Networking programmes prepare graduates to keep organisations connected through reliable infrastructure.")

# Business
add("business-administration", "BSc Business Administration", "Business & Economics",
    "Build broad management skills across marketing, finance, HR, and operations.",
    "Management; Marketing; Accounting basics; Organisational behaviour; Strategy",
    "Business manager; Entrepreneur; Management trainee",
    "Elective Mathematics; Economics; Accounting; English",
    "University of Ghana; KNUST; UCC; UPS",
    "Business Administration gives a versatile foundation for leading teams and organisations.")
add("accounting", "BSc Accounting", "Business & Economics",
    "Master financial reporting, auditing, and management accounting for organisations.",
    "Financial accounting; Cost accounting; Auditing; Taxation; Finance",
    "Accountant; Auditor; Tax associate; Financial analyst pathway",
    "Elective Mathematics; Accounting; Economics",
    "University of Ghana; KNUST; UCC; UPS",
    "Accounting programmes train students to measure and communicate financial performance with ethics and precision.")
add("banking-finance", "BSc Banking and Finance", "Business & Economics",
    "Understand banks, financial markets, investments, and corporate finance.",
    "Financial markets; Banking operations; Investment analysis; Risk; Corporate finance",
    "Bank officer; Credit analyst; Treasury associate",
    "Elective Mathematics; Economics; Accounting",
    "University of Ghana; KNUST; UCC; UPS",
    "Students learn how money moves through banks and markets, and how firms raise and manage capital.")
add("economics", "BA / BSc Economics", "Business & Economics",
    "Analyse how societies allocate resources using micro and macroeconomics.",
    "Microeconomics; Macroeconomics; Econometrics; Development economics",
    "Economist; Policy analyst; Research officer",
    "Elective Mathematics; Economics; Geography",
    "University of Ghana; KNUST; UCC",
    "Economics develops analytical tools for markets, policy, and development challenges.")
add("marketing", "BSc Marketing", "Business & Economics",
    "Create value for customers through branding, research, and digital marketing.",
    "Consumer behaviour; Market research; Brand management; Digital marketing",
    "Marketing executive; Brand associate; Digital marketer",
    "English; Economics; Elective Mathematics",
    "University of Ghana; KNUST; UCC",
    "Marketing programmes blend creativity and analytics to position products and reach audiences.")
add("human-resource-management", "BSc Human Resource Management", "Business & Economics",
    "Manage people systems: recruitment, performance, training, and labour relations.",
    "HR planning; Recruitment; Performance management; Labour law basics; Training",
    "HR officer; Talent associate; Employee relations officer",
    "English; Social Studies; Economics",
    "University of Ghana; KNUST; UCC; UPS",
    "HRM focuses on productive workplaces through fair policies and talent development.")
add("entrepreneurship", "BSc Entrepreneurship", "Business & Economics",
    "Launch and grow ventures with opportunity recognition, finance, and innovation skills.",
    "Opportunity analysis; Business models; Small business finance; Innovation",
    "Founder; Startup operator; SME consultant",
    "Economics; Elective Mathematics; English",
    "KNUST; University of Ghana; UCC",
    "Entrepreneurship programmes help students turn ideas into viable businesses.")
add("supply-chain-management", "BSc Logistics and Supply Chain Management", "Business & Economics",
    "Coordinate procurement, logistics, and inventory across local and global networks.",
    "Procurement; Logistics; Inventory; Operations; Trade facilitation",
    "Logistics officer; Procurement analyst; Supply chain coordinator",
    "Elective Mathematics; Economics; Geography",
    "KNUST; University of Ghana; UPS",
    "Supply chain education prepares graduates to move goods efficiently while managing cost and risk.")
add("actuarial-science", "BSc Actuarial Science", "Business & Economics",
    "Use mathematics and statistics to price risk in insurance and finance.",
    "Probability; Financial maths; Life contingencies; Statistics; Risk modelling",
    "Actuarial analyst; Risk analyst; Insurance analyst",
    "Elective Mathematics; Economics; Accounting",
    "KNUST; University of Ghana",
    "Actuarial science is highly quantitative — modelling uncertainty for pensions, insurance, and financial risk.")
add("hospitality-management", "BSc Hospitality Management", "Business & Economics",
    "Run hotels, tourism services, and guest experience operations.",
    "Front office; Food and beverage; Tourism; Hospitality marketing",
    "Hotel manager trainee; Events coordinator; Tourism officer",
    "English; Social Studies; Home Economics",
    "University of Cape Coast; University of Ghana",
    "Hospitality programmes combine service excellence with business operations for tourism.")
add("procurement", "BSc Procurement and Supply Chain", "Business & Economics",
    "Specialise in purchasing strategy, contracts, and supplier management.",
    "Procurement law basics; Supplier evaluation; Contract management; Negotiation",
    "Procurement officer; Buyer; Contract administrator",
    "Economics; Elective Mathematics; English",
    "KNUST; UPS; University of Ghana",
    "Procurement training emphasises value for money, ethics, and supplier relationships.")
add("insurance", "BSc Insurance", "Business & Economics",
    "Study risk transfer, underwriting, claims, and insurance markets.",
    "Principles of insurance; Underwriting; Claims; Risk management",
    "Insurance officer; Underwriter trainee; Claims associate",
    "Economics; Elective Mathematics; Accounting",
    "University of Ghana; KNUST",
    "Insurance programmes prepare graduates to help individuals and firms manage financial risk.")

# Natural Sciences
add("biological-sciences", "BSc Biological Sciences", "Natural Sciences",
    "Explore living systems from cells to ecosystems with laboratory practice.",
    "Cell biology; Genetics; Ecology; Microbiology; Biochemistry",
    "Lab scientist; Research assistant; Environmental biologist pathway",
    "Biology; Chemistry; Elective Mathematics",
    "KNUST; University of Ghana; UCC",
    "Biological Sciences builds life-science literacy for research, health pathways, and environmental careers.")
add("chemistry", "BSc Chemistry", "Natural Sciences",
    "Study matter, reactions, and chemical analysis in laboratory settings.",
    "Organic; Inorganic; Physical chemistry; Analytical chemistry",
    "Chemist; Lab analyst; Quality control chemist",
    "Chemistry; Physics; Elective Mathematics",
    "KNUST; University of Ghana; UCC",
    "Chemistry programmes train precise experimental skills used in industry, research, and regulation.")
add("physics", "BSc Physics", "Natural Sciences",
    "Investigate energy, matter, and physical laws with mathematical modelling.",
    "Mechanics; Electromagnetism; Modern physics; Laboratory physics",
    "Physicist pathway; Lab technologist; Technical analyst",
    "Physics; Elective Mathematics; Chemistry",
    "KNUST; University of Ghana; UCC",
    "Physics develops quantitative reasoning useful in technology, research, and engineering-adjacent roles.")
add("mathematics", "BSc Mathematics", "Natural Sciences",
    "Develop abstract and applied mathematical reasoning for science and industry.",
    "Algebra; Analysis; Discrete maths; Probability; Modelling",
    "Data roles; Teaching pathway; Quantitative analyst junior roles",
    "Elective Mathematics; Physics; ICT",
    "KNUST; University of Ghana; UCC",
    "Mathematics sharpens logical thinking that underpins computing, finance, teaching, and modelling.")
add("statistics", "BSc Statistics", "Natural Sciences",
    "Collect, analyse, and interpret data for research and decision-making.",
    "Probability; Inference; Regression; Survey methods; Computing for stats",
    "Statistician; Data analyst; Research officer",
    "Elective Mathematics; Economics; ICT",
    "KNUST; University of Ghana; UCC",
    "Statistics programmes prepare graduates to design studies and draw trustworthy conclusions from data.")
add("biochemistry", "BSc Biochemistry", "Natural Sciences",
    "Study the chemistry of life — proteins, metabolism, and molecular biology.",
    "Biomolecules; Metabolism; Molecular biology; Enzymology",
    "Biochemist; Lab scientist; Biotech research assistant",
    "Biology; Chemistry; Elective Mathematics",
    "KNUST; University of Ghana",
    "Biochemistry links chemistry and biology for labs, health sciences, and biotechnology.")
add("environmental-science", "BSc Environmental Science", "Natural Sciences",
    "Analyse environmental problems and sustainability solutions.",
    "Ecology; Pollution; GIS basics; Environmental policy; Field methods",
    "Environmental officer; Sustainability associate; Conservation roles",
    "Biology; Chemistry; Geography",
    "KNUST; University of Ghana; UCC; UENR",
    "Environmental Science combines field and lab work to support sustainable development.")
add("food-science", "BSc Food Science and Technology", "Natural Sciences",
    "Apply science to food safety, processing, and product development.",
    "Food chemistry; Microbiology; Processing; Quality assurance",
    "Food technologist; QA officer; Product development associate",
    "Biology; Chemistry; Elective Mathematics; Home Economics",
    "KNUST; University of Ghana; UCC",
    "Food science prepares graduates for safe and innovative food products in industry and regulation.")

# Agriculture
add("agriculture", "BSc Agriculture", "Agriculture & Environment",
    "Improve crop and livestock systems for food security and rural livelihoods.",
    "Crop science; Soil science; Animal science; Agribusiness basics",
    "Agronomist; Extension officer; Farm manager",
    "Biology; Chemistry; Geography; Elective Mathematics",
    "KNUST; UCC; UDS; UENR",
    "Agriculture programmes blend science and practice so graduates can raise productivity sustainably.")
add("agricultural-engineering", "BSc Agricultural Engineering", "Agriculture & Environment",
    "Engineer tools, irrigation, and post-harvest systems for farming.",
    "Farm power; Irrigation; Soil and water engineering; Processing equipment",
    "Agricultural engineer; Irrigation engineer",
    "Elective Mathematics; Physics; Chemistry",
    "KNUST; UCC",
    "Agricultural engineering applies mechanical and civil principles to farm productivity.")
add("natural-resources", "BSc Natural Resources Management", "Agriculture & Environment",
    "Manage forests, wildlife, and land resources responsibly.",
    "Forestry; Wildlife; Land use; Conservation; Resource economics",
    "Resource officer; Forestry roles; Conservation associate",
    "Biology; Geography; Chemistry",
    "KNUST; UENR; UCC",
    "Students learn stewardship of forests, water, and biodiversity alongside community livelihoods.")
add("aquaculture", "BSc Aquaculture and Fisheries", "Agriculture & Environment",
    "Produce and manage fish and aquatic resources sustainably.",
    "Fish biology; Pond management; Hatchery; Aquatic ecology",
    "Aquaculture officer; Fisheries officer",
    "Biology; Chemistry; Geography",
    "UCC; KNUST; UDS",
    "Aquaculture supports Ghana’s blue economy through sustainable fish production.")
add("agribusiness", "BSc Agribusiness", "Agriculture & Environment",
    "Run agricultural value chains with business and market skills.",
    "Farm business; Value chains; Agricultural marketing; Finance",
    "Agribusiness manager; Commodity trader junior roles",
    "Economics; Elective Mathematics; Agriculture Elective",
    "KNUST; UCC; UDS",
    "Agribusiness connects farming to markets through finance, logistics, and entrepreneurship.")
add("climate-science", "BSc Meteorology and Climate Science", "Agriculture & Environment",
    "Understand climate systems and adaptation strategies for communities.",
    "Climatology; Meteorology basics; Adaptation; Environmental monitoring",
    "Climate officer; Environmental analyst",
    "Geography; Physics; Elective Mathematics; Biology",
    "UENR; University of Ghana; KNUST",
    "These programmes prepare graduates to interpret climate data and support adaptation planning.")

# Built Environment
add("architecture", "BSc Architecture", "Built Environment",
    "Design buildings and spaces that are functional, safe, and culturally responsive.",
    "Design studio; Building technology; History and theory; Structures intro",
    "Architectural assistant; Design technologist pathway",
    "Elective Mathematics; Physics; Visual Arts; Technical Drawing",
    "KNUST",
    "Architecture blends creativity and technical knowledge through studio-based learning.")
add("quantity-surveying", "BSc Quantity Surveying", "Built Environment",
    "Manage construction costs, contracts, and project finances.",
    "Measurement; Cost planning; Contracts; Construction economics",
    "Quantity surveyor; Cost consultant; Project cost officer",
    "Elective Mathematics; Economics; Technical Drawing",
    "KNUST; technical universities",
    "Quantity surveying keeps construction projects financially controlled from tender to completion.")
add("planning", "BSc Human Settlement Planning", "Built Environment",
    "Plan towns and regions for orderly, sustainable development.",
    "Urban planning; Land use; GIS; Planning law basics",
    "Planning officer; Urban development associate",
    "Geography; Elective Mathematics; Economics",
    "KNUST; University of Ghana",
    "Planning programmes train graduates to shape cities through policy, maps, and engagement.")
add("land-economy", "BSc Land Economy", "Built Environment",
    "Study land markets, valuation, and real estate economics.",
    "Valuation; Land law basics; Real estate; Economics of land",
    "Valuer trainee; Estate officer; Land administration roles",
    "Economics; Elective Mathematics; Geography",
    "KNUST",
    "Land Economy connects property markets with law and valuation.")
add("construction-technology", "BSc Construction Technology and Management", "Built Environment",
    "Deliver building projects through construction methods and site management.",
    "Building materials; Site management; Construction methods; Safety",
    "Site engineer trainee; Construction supervisor",
    "Elective Mathematics; Physics; Technical Drawing",
    "KNUST; technical universities",
    "Construction programmes emphasise practical delivery with quality, safety, and scheduling.")

# Education
add("education-basic", "BEd Basic Education", "Education",
    "Prepare to teach and support learning at the basic school level.",
    "Pedagogy; Curriculum; Child development; Subject methods; Teaching practice",
    "Basic school teacher; Education officer pathway",
    "English; Social Studies; relevant electives",
    "UEW; UCC; University of Ghana",
    "Basic Education degrees combine subject knowledge with classroom practice.")
add("education-secondary", "BEd Secondary Education", "Education",
    "Train as a secondary school teacher in specialised subject areas.",
    "Subject pedagogy; Assessment; Educational psychology; Teaching practice",
    "SHS teacher; Subject tutor",
    "Strong SHS electives in teaching subject; English",
    "UEW; UCC; University of Ghana",
    "Secondary education programmes deepen content knowledge and classroom skills for SHS teaching.")
add("early-childhood", "BEd Early Childhood Education", "Education",
    "Support learning and care for young children in the early years.",
    "Child development; Play-based learning; Early literacy and numeracy; Care practices",
    "Early childhood educator; Kindergarten teacher",
    "English; Social Studies; Home Economics",
    "UEW; UCC",
    "Early childhood programmes emphasise nurturing environments for lifelong learning foundations.")
add("special-education", "BEd Special Education", "Education",
    "Teach and support learners with diverse educational needs.",
    "Inclusive education; Assessment; Intervention strategies; Psychology",
    "Special educator; Inclusive education officer",
    "English; Social Studies; Biology",
    "UEW; UCC",
    "Special Education prepares teachers to adapt instruction so every learner can progress.")

# Social Sciences
add("psychology", "BA / BSc Psychology", "Social Sciences & Arts",
    "Study behaviour and mental processes with research and applied foundations.",
    "Developmental; Social; Cognitive; Research methods; Counselling intro",
    "HR and people roles; Research assistant; Counselling pathway (further study)",
    "English; Social Studies; Biology; Elective Mathematics",
    "University of Ghana; UCC; KNUST",
    "Psychology builds insight into human behaviour useful in education, health, and business.")
add("sociology", "BA Sociology", "Social Sciences & Arts",
    "Analyse social structures, change, and community life.",
    "Social theory; Research methods; Ghanaian society; Development sociology",
    "Social researcher; NGO programme officer; Policy support roles",
    "English; Social Studies; Geography",
    "University of Ghana; UCC",
    "Sociology helps graduates understand institutions and inequality in development work.")
add("political-science", "BA Political Science", "Social Sciences & Arts",
    "Study government, power, and public affairs.",
    "Political theory; Comparative politics; Ghanaian politics; International relations intro",
    "Public service; Policy analyst; Diplomatic pathway",
    "English; Social Studies; Government",
    "University of Ghana; UCC; KNUST",
    "Political Science prepares students for civic leadership and careers around governance.")
add("geography-development", "BA Geography and Resource Development", "Social Sciences & Arts",
    "Explore people–environment relationships and spatial development.",
    "Physical geography; Human geography; GIS basics; Development studies",
    "Development officer; GIS assistant; Planning support",
    "Geography; Elective Mathematics; Economics",
    "University of Ghana; UCC; KNUST",
    "Geography programmes combine maps, fieldwork, and development thinking.")
add("social-work", "BA Social Work", "Social Sciences & Arts",
    "Support individuals and communities through professional social services.",
    "Social welfare; Casework; Community practice; Ethics",
    "Social worker; Community development officer",
    "English; Social Studies",
    "University of Ghana; UCC",
    "Social Work trains practitioners to advocate for vulnerable people and deliver support.")
add("history", "BA History", "Social Sciences & Arts",
    "Investigate the past to understand societies and identity.",
    "African history; World history; Historical methods; Ghanaian history",
    "Teaching pathway; Heritage and museum roles; Research",
    "English; Social Studies; History",
    "University of Ghana; UCC",
    "History develops critical reading and writing skills for education and culture careers.")
add("languages", "BA English / French / Linguistics", "Social Sciences & Arts",
    "Deepen language skills for communication, teaching, and cultural work.",
    "Literature; Linguistics; Composition; Language teaching methods",
    "Teacher; Communications; Translation pathway",
    "English; French; Literature",
    "University of Ghana; UCC; UEW",
    "Language programmes build advanced communication and cultural literacy.")
add("international-relations", "BA International Relations", "Social Sciences & Arts",
    "Study diplomacy, global politics, and international organisations.",
    "IR theory; Diplomacy; International organisations; Global political economy",
    "Foreign service pathway; NGO international programmes; Policy roles",
    "English; Government; Social Studies; Economics",
    "University of Ghana; UCC",
    "International Relations prepares students to analyse global affairs and development work.")

# Creative
add("communication-studies", "BA Communication Studies", "Creative Arts & Communication",
    "Create and manage media messages across journalism, PR, and digital platforms.",
    "Media writing; PR; Broadcasting basics; Digital media; Media ethics",
    "Journalist; PR officer; Content producer",
    "English; Social Studies; Literature",
    "University of Ghana; UCC; GIJ pathways",
    "Communication Studies trains clear storytelling for newsrooms, brands, and public institutions.")
add("fine-art", "BA Fine Art", "Creative Arts & Communication",
    "Develop studio practice in drawing, painting, sculpture, and visual expression.",
    "Studio practice; Art history; Critique; Contemporary practice",
    "Artist; Illustrator; Creative educator pathway",
    "Visual Arts; English",
    "KNUST; University of Education",
    "Fine Art centres creative practice and critical thinking through intensive studio work.")
add("graphic-design", "BA Communication Design", "Creative Arts & Communication",
    "Design visual identities, publications, and digital interfaces.",
    "Typography; Branding; Layout; Digital design tools; Design thinking",
    "Graphic designer; Brand designer; UI design pathway",
    "Visual Arts; ICT; English",
    "KNUST",
    "Design programmes teach how visuals communicate clearly for business, culture, and the web.")
add("theatre-film", "BA Theatre Arts / Film and Television", "Creative Arts & Communication",
    "Tell stories through performance, directing, and screen production.",
    "Acting and directing; Scriptwriting; Production; Media aesthetics",
    "Performer; Production assistant; Content creator",
    "English; Literature; Visual Arts",
    "University of Ghana; NAFTI pathways; UCC",
    "These programmes blend creative storytelling with production skills for stage and screen.")
add("music", "BA Music", "Creative Arts & Communication",
    "Study performance, theory, and musicology with practical ensembles.",
    "Music theory; Performance; Ethnomusicology; Composition basics",
    "Performer; Music educator; Studio roles",
    "Music; English",
    "University of Ghana; UEW",
    "Music degrees combine artistry and scholarship for performance, teaching, and culture.")
add("publishing", "BA Publishing Studies", "Creative Arts & Communication",
    "Manage the journey of text from manuscript to reader across print and digital.",
    "Editing; Book design basics; Publishing business; Digital publishing",
    "Editorial assistant; Publishing officer",
    "English; Literature; ICT",
    "KNUST",
    "Publishing Studies prepares graduates for editorial and production roles in knowledge industries.")

# Law
add("law-llb", "LLB Law", "Law",
    "Study the legal system, rights, and legal reasoning for advocacy and counsel.",
    "Constitutional law; Contract; Criminal law; Tort; Legal method",
    "Lawyer pathway (after professional training); Legal officer; Compliance",
    "English; Literature; Government; Elective Mathematics helpful",
    "University of Ghana; KNUST; UCC; GIMPA",
    "An LLB builds rigorous legal analysis. Graduates usually continue to professional training before practice.")


def duration_for(name: str) -> str:
    if any(k in name for k in ("MBChB", "Veterinary", "Dental", "Pharmacy", "Doctor of Pharmacy", "DVM")):
        return "6 years"
    return "4 years"


def main() -> None:
    programmes = []
    for slug, name, field, brief, topics, careers, shs, unis, detail in RAW:
        programmes.append(
            {
                "slug": slug,
                "name": name,
                "field": field,
                "level": "Undergraduate (Bachelor's)",
                "typical_duration": duration_for(name),
                "brief": brief,
                "core_topics": [t.strip() for t in topics.split(";") if t.strip()],
                "career_paths": [t.strip() for t in careers.split(";") if t.strip()],
                "related_shs_subjects": [t.strip() for t in shs.split(";") if t.strip()],
                "commonly_offered_at": [t.strip() for t in unis.split(";") if t.strip()],
                "detailed_overview": detail,
            }
        )

    slugs = [p["slug"] for p in programmes]
    dupes = sorted({s for s in slugs if slugs.count(s) > 1})
    if dupes:
        raise SystemExit(f"Duplicate slugs: {dupes}")

    fields = [f for f in FIELDS_ORDER if any(p["field"] == f for p in programmes)]
    payload = {
        "note": (
            "Course Directory reference catalogue for Atlas. Educational overview only — "
            "no cut-offs or eligibility claims. Expand by appending programmes."
        ),
        "fields": fields,
        "programmes": programmes,
    }
    out = Path(__file__).resolve().parents[1] / "data" / "course_directory.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out} programmes={len(programmes)} fields={len(fields)}")


if __name__ == "__main__":
    main()
