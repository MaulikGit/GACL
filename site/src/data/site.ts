// Site-wide content for the GACL redesign.
// Facts, figures, names and addresses come from the crawl of gacl.com
// (scrape/output); descriptive copy is written fresh for the new site.

export const company = {
  name: "Gujarat Alkalies and Chemicals Limited",
  short: "GACL",
  tagline: "Promoting Green Technology",
  promoter: "Promoted by Govt. of Gujarat",
  founded: 1973,
  cin: "L24110GJ1973PLC002247",
  gstin: "24AAACG8896M1ZX",
  phone: "+91 265 6111000",
  fax: "+91 265 6111012",
  emails: {
    marketing: "headmarketing@gacl.co.in",
    export: "export@gacl.co.in",
    purchase: "purchase@gacl.co.in",
    investor: "investor_relations@gacl.co.in",
    feedback: "feedback@gacl.co.in",
  },
  social: {
    linkedin: "https://www.linkedin.com/company/gujarat-alkalies-and-chemicals-limited",
    facebook: "https://www.facebook.com/",
    instagram: "https://www.instagram.com/",
    youtube: "https://www.youtube.com/",
  },
};

export type NavItem = { label: string; href: string; desc?: string };
export type NavGroup = { label: string; href: string; items: NavItem[]; feature?: { title: string; text: string; href: string } };

export const nav: NavGroup[] = [
  {
    label: "Company",
    href: "/company/",
    items: [
      { label: "The Corporate World", href: "/company/", desc: "Who we are and what we make" },
      { label: "Corporate Philosophy", href: "/company/philosophy/", desc: "Vision, mission and values" },
      { label: "Governing Body", href: "/company/governing-body/", desc: "Our Board of Directors" },
      { label: "Our Journey", href: "/company/journey/", desc: "Five decades of milestones" },
      { label: "Honours & Recognitions", href: "/company/honours/", desc: "Awards and certifications" },
    ],
    feature: { title: "Since 1973", text: "From 37,425 TPA to 8,52,400 TPA of caustic soda capacity.", href: "/company/journey/" },
  },
  {
    label: "Products",
    href: "/products/",
    items: [], // filled from product groups
  },
  {
    label: "Sustainability",
    href: "/sustainability/",
    items: [
      { label: "Environment", href: "/sustainability/", desc: "Renewables, green hydrogen, clean tech" },
      { label: "Safety & Health", href: "/sustainability/safety/", desc: "Our ‘No Harm’ commitment" },
      { label: "CSR", href: "/sustainability/csr/", desc: "GACL Foundation Trust programmes" },
      { label: "Governance & Certificates", href: "/sustainability/governance/", desc: "ISO, BIS, NSF and BRSR" },
    ],
  },
  {
    label: "Investors",
    href: "/investors/",
    items: [
      { label: "Investor Centre", href: "/investors/", desc: "Financials, filings and reports" },
      { label: "Investors Connect", href: "/investors/#connect", desc: "Grievance redressal contact" },
    ],
  },
  {
    label: "Partners",
    href: "/partners/",
    items: [
      { label: "Materials & Services", href: "/partners/", desc: "Vendor registration and raw materials" },
      { label: "Tenders", href: "/partners/tenders/", desc: "Open tenders and EOIs" },
      { label: "Dealer Network", href: "/partners/dealers/", desc: "Authorised dealers across India" },
    ],
  },
  {
    label: "Careers",
    href: "/careers/",
    items: [],
  },
  {
    label: "Media",
    href: "/media/",
    items: [],
  },
];

export const stats = [
  { value: 852400, display: "8,52,400", suffix: " TPA", label: "Caustic soda capacity, 2nd largest in India (incl. subsidiary)" },
  { value: 60, suffix: "+", label: "Countries our products reach" },
  { value: 35, suffix: "+", label: "Products across ten product groups" },
  { value: 5000, display: "5,000", suffix: "+", label: "Customers, from MSMEs to global majors" },
];

export const highlights = [
  {
    title: "India’s first membrane cell plant",
    text: "In 1989 GACL became the first Indian company to replace mercury cell technology with membrane cell electrolysis.",
    icon: "spark",
  },
  {
    title: "208 MW of renewable power",
    text: "171.45 MW of wind and 36.62 MW of solar capacity for captive use, with 100 MW more planned with NTPC REL.",
    icon: "leaf",
  },
  {
    title: "Patented Hydrazine Hydrate",
    text: "An indigenous process developed with CSIR-IICT, patented in India and the US, now running at 10,000 MTA at Dahej.",
    icon: "flask",
  },
  {
    title: "Four complexes in Gujarat",
    text: "Integrated sites at Vadodara (Ranoli and Coelho) and Dahej, close to raw materials, ports and rail.",
    icon: "factory",
  },
];

export const industries = [
  { name: "Soaps & Detergents", groups: ["Caustic Soda", "Caustic Potash", "Phosphoric Acid"] },
  { name: "Agrochemicals", groups: ["Caustic Potash", "Chlorine Derivatives", "Hydrazine Hydrate"] },
  { name: "Water Treatment", groups: ["Poly Aluminium Chloride", "Stable Bleaching Powder", "Chlorine"] },
  { name: "Pulp & Paper", groups: ["Sodium Chlorate", "Hydrogen Peroxide", "Caustic Soda"] },
  { name: "Pharmaceuticals", groups: ["Chloromethanes", "Caustic Soda", "Caustic Potash"] },
  { name: "Textiles", groups: ["Hydrogen Peroxide", "Caustic Soda", "Chlorine Derivatives"] },
];

export const sectors = [
  "Textiles", "Aluminium", "Pharmaceuticals", "Water Treatment", "Rubber", "Soaps & Detergents",
  "Paper", "Dyes", "Sugar", "Edible Oil", "Beverages", "PVC", "Polymers", "Leather", "Glass",
  "Petroleum", "Agrochemicals", "Fertilizers", "Paint", "Refrigerants", "Fragrance", "Metals",
];

export const philosophy = {
  vision: "To continue to be identified and recognised as a dynamic, modern and eco-friendly chemical company with enduring ethics and values.",
  mission: "To run our business responsibly towards every stakeholder — customers, employees, shareholders, society and the environment — through technology, safety and quality.",
  values: [
    { title: "Integrity", text: "Transparent, honest and accountable in every interaction, inside and outside the company.", icon: "shield" },
    { title: "Excellence", text: "World-class technology, quality and operating discipline across every plant.", icon: "spark" },
    { title: "Corporate Governance", text: "Clear accountability to our Board, shareholders and the Government of Gujarat.", icon: "scale" },
    { title: "Social Responsibility", text: "Lasting improvements in the health, education and livelihoods of our communities.", icon: "heart" },
  ],
};

export const board = [
  { name: "Dr. Hasmukh Adhia, IAS (Retd.)", role: "Chairman" },
  { name: "Smt. Avantika Singh, IAS", role: "Managing Director" },
  { name: "Dr. T Natarajan, IAS", role: "Director" },
  { name: "Shri Bimal Julka, IAS (Retd.)", role: "Independent Director" },
  { name: "Shri Nitin Shukla", role: "Independent Director" },
  { name: "Smt. Shridevi Shukla", role: "Independent Director" },
  { name: "Dr. Chinmay Ghoroi", role: "Independent Director" },
  { name: "Shri Sanjay Joshi", role: "Independent Director" },
];

export type Milestone = { year: number; title: string; points: string[]; tag?: "growth" | "green" | "first" | "award" };

export const journey: Milestone[] = [
  { year: 2025, tag: "growth", title: "India’s largest chlorotoluenes plant", points: ["30,000 TPA chlorotoluenes plant at Dahej dedicated to the nation.", "First dispatches of Benzyl Chloride (April) and Benzyl Alcohol & Benzaldehyde (July).", "First PAC-30 powder shipped from the 9,900 MTA Coelho Complex plant."] },
  { year: 2023, tag: "first", title: "Import substitutes reach the market", points: ["First dispatches of Hydrazine Hydrate (80%) and Purified Phosphoric Acid (85%), including food grade.", "Commissioned a 700 MTPD caustic evaporation unit, one of India’s largest.", "National award for the Dahej Complex under PAT Cycle II (NMEEE)."] },
  { year: 2022, tag: "growth", title: "Dahej expansion dedicated by the Prime Minister", points: ["1,05,000 TPA chloromethanes complex and caustic soda expansion from 785 to 1,310 TPD.", "10,000 MTA Hydrazine Hydrate plant and GNAL’s 800 TPD caustic soda plant with 130 MW power.", "US patent granted for the indigenous Hydrazine Hydrate process."] },
  { year: 2021, tag: "first", title: "First BIS licence for Ortho Phosphoric Acid", points: ["MoU with GAIL for a 500 KLD bioethanol plant in Gujarat.", "Joint 20-year patent with CSIR for an improved Hydrazine Hydrate process."] },
  { year: 2020, tag: "green", title: "35 MW of solar at Charanka", points: ["Another 12.5 MW solar project commissioned at Charanka.", "New 15,000 TPA stable bleaching powder and 16,500 TPA aluminium chloride plants at Dahej."] },
  { year: 2018, tag: "growth", title: "Coelho Complex and PAC", points: ["32,000 TPA Poly Aluminium Chloride plant starts at the Coelho Complex, Vadodara.", "Chloromethanes capacity raised from 37,950 to 56,100 TPA; 14,000 TPA Hydrogen Peroxide Plant-III at Dahej."] },
  { year: 2017, tag: "green", title: "171.45 MW of wind power", points: ["Phase X wind farm takes total wind capacity to 171.45 MW.", "Energy-efficient electrolyser elements installed at Dahej."] },
  { year: 2015, tag: "growth", title: "GACL–NALCO joint venture", points: ["GNAL formed with NALCO for an 800 TPD caustic soda plant and 130 MW power plant.", "First company to move caustic soda by rail from western to southern and eastern India."] },
  { year: 2014, tag: "first", title: "India’s first sodium chlorate maker", points: ["20,000 TPA sodium chlorate plant commissioned at Dahej."] },
  { year: 2008, tag: "green", title: "Wind power and cleaner chemistry", points: ["23.75 MW wind farm at Moti Sindhodi, Kutch.", "First in India to adopt the Sulphate Removal System at Dahej."] },
  { year: 1996, tag: "growth", title: "Into hydrogen peroxide", points: ["First 11,000 TPA hydrogen peroxide plant at Vadodara."] },
  { year: 1995, tag: "growth", title: "Dahej Complex begins", points: ["26,730 TPA phosphoric acid plant starts production at Dahej."] },
  { year: 1989, tag: "first", title: "Mercury cell to membrane cell", points: ["First Indian company to adopt eco-friendly membrane cell technology."] },
  { year: 1976, tag: "growth", title: "Production starts at Vadodara", points: ["Caustic soda plant commissioned with 37,425 TPA capacity."] },
  { year: 1973, tag: "growth", title: "GACL is incorporated", points: ["Promoted by the Government of Gujarat through GIIC, at Ranoli, Vadodara."] },
];

export const honours = [
  { year: 2025, title: "National CSR Award", by: "World HRD Congress", text: "For GACL Foundation Trust’s Home for Mentally Differently-abled Children project." },
  { year: 2025, title: "Certificate of Merit, Safety Awards", by: "National Safety Council of India", text: "Vadodara Complex, for occupational safety & health performance in 2022–24." },
  { year: 2024, title: "1st Prize, GEO Excellence Awards", by: "GEO Excellence Awards", text: "For CSR initiatives." },
  { year: 2023, title: "National Award, PAT Cycle II", by: "Bureau of Energy Efficiency (NMEEE)", text: "Top performer in the chlor-alkali sector, Dahej Complex." },
  { year: 2021, title: "Excellence in Cost Management", by: "Institute of Cost Accountants of India", text: "Third consecutive year." },
  { year: 2013, title: "Best CSR Practice", by: "BSE Social & Corporate Governance Awards", text: "For community programmes." },
  { year: 2012, title: "National Safety Award", by: "Ministry of Labour & Employment", text: "For excellent safety standards." },
  { year: 2008, title: "National Energy Conservation Award", by: "Ministry of Power", text: "Fifth consecutive time." },
];

export const certificates = [
  { code: "ISO 9001:2015", label: "Quality management" },
  { code: "ISO 14001:2015", label: "Environmental management" },
  { code: "ISO 45001:2018", label: "Occupational health & safety" },
  { code: "ISO 50001:2018", label: "Energy management" },
  { code: "ISO 27001:2022", label: "Information security" },
  { code: "FSSAI", label: "Food grade phosphoric acid" },
  { code: "BIS", label: "Ortho phosphoric acid" },
  { code: "NSF", label: "Poly aluminium chloride" },
];

export const locations = [
  {
    name: "Registered Office & Vadodara Complex",
    sub: "Includes the Coelho Complex",
    address: "P.O. Ranoli – 391 350, Vadodara, Gujarat, India",
    phones: ["+91 265 6111000"],
    fax: "+91 265 6111012",
    map: "https://www.google.com/maps/search/?api=1&query=Gujarat+Alkalies+and+Chemicals+Ranoli+Vadodara",
  },
  {
    name: "Dahej Complex – 1",
    sub: "Caustic soda, peroxides, chlorates, phosphoric acid",
    address: "P.O. Dahej – 392 130, Taluka Vagra, Dist. Bharuch, Gujarat, India",
    phones: ["+91 2641 613200 (Reception)", "+91 2641 613256 (Security)"],
    map: "https://www.google.com/maps/search/?api=1&query=GACL+Dahej+Complex+Bharuch",
  },
  {
    name: "Dahej Complex – 2",
    sub: "GIDC Dahej PCPIR",
    address: "Plot No. DII/9, GIDC Dahej, PCPIR, Near GNFC-TDI Plant, Village Rahiad, Taluka Vagra, Dist. Bharuch, Gujarat – 392 130, India",
    phones: [],
    map: "https://www.google.com/maps/search/?api=1&query=GIDC+Dahej+PCPIR+Rahiad",
  },
];

export const news = [
  { date: "2025-07-05", title: "First dispatch of Benzyl Alcohol and Benzaldehyde from India’s largest chlorotoluenes plant", href: "https://gacl.com/gacl-flags-off-first-dispatch-of-benzyl-alcohol-and-benzaldehyde-from-indias-largest-chlorotoluenes-plant/" },
  { date: "2025-04-21", title: "First dispatch of Benzyl Chloride from the 30,000 TPA chlorotoluenes plant at Dahej", href: "https://gacl.com/gacl-flags-off-first-dispatch-of-benzyl-chloride-from-indias-largest-chlorotoluenes-plant/" },
  { date: "2025-03-29", title: "Chief Minister of Gujarat dedicates the country’s largest chlorotoluenes plant to the nation", href: "https://gacl.com/gacl-news/" },
];

export const investorLinks = [
  { title: "Financials", text: "Annual reports and quarterly financial results.", href: "https://gacl.com/financials/", icon: "chart" },
  { title: "Shareholding Pattern", text: "Quarterly shareholding disclosures.", href: "https://gacl.com/shareholding-pattern/", icon: "pie" },
  { title: "Corporate Governance", text: "Policies, codes and committee reports.", href: "https://gacl.com/corporate-governance/", icon: "scale" },
  { title: "Credit Rating", text: "Ratings from credit rating agencies.", href: "https://gacl.com/credit-rating/", icon: "badge" },
  { title: "BRSR Reports", text: "Business Responsibility & Sustainability Reports.", href: "https://gacl.com/brsr-reports/", icon: "leaf" },
  { title: "Other Information", text: "Notices, disclosures and investor campaigns.", href: "https://gacl.com/other-financial-information/", icon: "doc" },
];

export const investorContact = {
  name: "Shri S. S. Bhatt",
  role: "Company Secretary & CGM (Legal, CC & CSR)",
  address: "Gujarat Alkalies and Chemicals Limited, P.O. Ranoli – 391 350, Dist. Vadodara, Gujarat, India",
  phone: "0265-6111000",
  fax: "0265-6111012",
  email: "investor_relations@gacl.co.in",
};

export const vendorLinks = [
  { title: "Vendor Pre-Qualification", text: "Qualify to supply goods and services to GACL.", href: "https://gacl.com/vendor-prequalification/", icon: "check" },
  { title: "Online Vendor Registration", text: "Register your company as a GACL vendor.", href: "https://gacl.com/online-vendor-registration/", icon: "user" },
  { title: "Salt Vendor Registration", text: "Supply salt, our primary raw material.", href: "https://gacl.com/salt-vendor-registration/", icon: "cube" },
  { title: "Major Raw Materials", text: "What we buy and in what volumes.", href: "https://gacl.com/major-raw-materials/", icon: "flask" },
  { title: "Scrap for Disposal", text: "Current lots of scrap material on offer.", href: "https://gacl.com/scrap-for-disposal/", icon: "recycle" },
];

export const quickLogins = [
  { label: "Dealers / Customers Login", href: "https://gacl.com/" },
  { label: "Vendors Login", href: "https://gacl.com/" },
  { label: "Customer Registration", href: "https://gacl.com/" },
  { label: "Contractors Login", href: "https://gacl.com/" },
  { label: "Employees Login", href: "https://gacl.com/" },
];
