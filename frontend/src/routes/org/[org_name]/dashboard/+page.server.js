export async function load({ params }) {
	//const post = await getPostFromDatabase(params.slug);

	const stories = [
		{
			name: 'Rising Waters',
			location: 'New Orleans',
			topic: 'Climate Change',
			text: 'Local communities joined forces to build innovative floating gardens, adapting to rising sea levels while creating new sustainable food sources for the neighborhood.',
			date: '2023-04-15'
		},
		{
			name: 'Digital Divide',
			location: 'Rural Montana',
			topic: 'Technology Access',
			text: 'Students created a mesh network using recycled equipment, bringing internet access to remote farms and enabling distance learning opportunities for isolated families.',
			date: '2023-06-22'
		},
		{
			name: 'Green Alleys',
			location: 'Chicago',
			topic: 'Urban Environment',
			text: 'Residents transformed neglected alleyways into green corridors with permeable surfaces, reducing flooding and creating safe walking paths between neighborhoods.',
			date: '2023-05-10'
		},
		{
			name: 'Senior Tech Squad',
			location: 'Miami',
			topic: 'Digital Literacy',
			text: 'High school volunteers partnered with retirement communities to provide technology training, helping seniors connect with family and access essential services online.',
			date: '2023-07-03'
		},
		{
			name: 'Community Fridge',
			location: 'Philadelphia',
			topic: 'Food Security',
			text: 'A network of community refrigerators placed throughout the city allows residents to donate and take food freely, reducing waste and addressing immediate hunger needs.',
			date: '2023-03-28'
		},
		{
			name: 'Youth Mentorship Program',
			location: 'Chicago',
			topic: 'Education',
			text: 'Local professionals volunteer weekly to mentor high school students, providing career guidance and academic support in underserved communities.',
			date: '2023-05-10'
		},
		{
			name: 'Urban Farm Initiative',
			location: 'Philadelphia',
			topic: 'Food Security',
			text: 'Abandoned lots transformed into productive urban farms, providing fresh produce and job training for neighborhood residents.',
			date: '2023-04-15'
		},
		{
			name: 'Renewable Energy Co-op',
			location: 'Rural Montana',
			topic: 'Climate Change',
			text: 'Farmers pooled resources to install shared wind turbines, reducing energy costs and creating a sustainable power source for the community.',
			date: '2023-06-22'
		},
		{
			name: 'Digital Inclusion Workshop',
			location: 'Miami',
			topic: 'Technology Access',
			text: 'Weekly workshops at the public library help residents learn essential computer skills and navigate online government services.',
			date: '2023-07-03'
		},
		{
			name: 'Intergenerational Story Exchange',
			location: 'New Orleans',
			topic: 'Cultural Preservation',
			text: 'Monthly gatherings bring elders and youth together to share family histories and traditional cultural practices.',
			date: '2023-03-28'
		},
		{
			name: 'Green Roof Project',
			location: 'Chicago',
			topic: 'Urban Environment',
			text: 'Local businesses collaborated to install green roofs throughout the downtown area, reducing urban heat island effects and managing stormwater.',
			date: '2023-05-10'
		},
		{
			name: 'Tech Recycling Drive',
			location: 'Philadelphia',
			topic: 'Technology Access',
			text: 'Community-wide initiative collects and refurbishes outdated devices, distributing them to families without home computers.',
			date: '2023-04-15'
		},
		{
			name: 'Disaster Preparedness Network',
			location: 'New Orleans',
			topic: 'Climate Change',
			text: 'Neighborhood groups organized block-by-block emergency response teams to improve resilience during increasingly frequent flood events.',
			date: '2023-06-22'
		},
		{
			name: 'Mobile Health Clinic',
			location: 'Rural Montana',
			topic: 'Healthcare Access',
			text: 'Volunteer medical professionals travel to remote areas providing preventive care and health screenings for underserved populations.',
			date: '2023-07-03'
		},
		{
			name: 'Cultural Food Exchange',
			location: 'Miami',
			topic: 'Cultural Preservation',
			text: 'Monthly potluck dinners showcase traditional recipes from the diverse cultural backgrounds represented in the neighborhood.',
			date: '2023-03-28'
		},
		{
			name: 'Affordable Housing Coalition',
			location: 'Philadelphia',
			topic: 'Housing',
			text: 'Residents successfully advocated for inclusive zoning regulations ensuring new developments include affordable housing units.',
			date: '2023-05-10'
		},
		{
			name: 'Youth Environmental Leaders',
			location: 'Chicago',
			topic: 'Urban Environment',
			text: 'Student-led initiative conducts regular cleanup events and educational workshops about local ecological systems.',
			date: '2023-04-15'
		},
		{
			name: 'Rural Broadband Expansion',
			location: 'Rural Montana',
			topic: 'Technology Access',
			text: 'Community cooperative established high-speed internet infrastructure for previously unserved farming communities.',
			date: '2023-06-22'
		},
		{
			name: 'Sustainable Transportation Plan',
			location: 'New Orleans',
			topic: 'Urban Environment',
			text: 'Comprehensive bike lane network and improved public transit options reduced car dependency and improved air quality.',
			date: '2023-07-03'
		},
		{
			name: 'Elder Care Network',
			location: 'Miami',
			topic: 'Healthcare Access',
			text: 'Volunteer coordination system ensures homebound seniors receive regular visits, medication reminders, and assistance with daily needs.',
			date: '2023-03-28'
		},
		{
			name: 'Community Mural Project',
			location: 'Philadelphia',
			topic: 'Cultural Preservation',
			text: 'Local artists collaborated with residents to create public murals celebrating the neighborhoods diverse history and cultural identity.',
			date: '2023-05-10'
		},
		{
			name: 'Food Recovery Program',
			location: 'Chicago',
			topic: 'Food Security',
			text: 'Partnership between restaurants and shelters redirects excess prepared food to those in need, reducing waste and hunger simultaneously.',
			date: '2023-04-15'
		},
		{
			name: 'Rural Medical Transportation',
			location: 'Rural Montana',
			topic: 'Healthcare Access',
			text: 'Volunteer driver network ensures rural residents can access medical appointments in distant healthcare facilities.',
			date: '2023-06-22'
		},
		{
			name: 'Climate-Resilient Infrastructure',
			location: 'New Orleans',
			topic: 'Climate Change',
			text: 'Community-driven initiative to retrofit existing buildings with flood-resistant features and elevated mechanical systems.',
			date: '2023-07-03'
		},
		{
			name: 'Digital Literacy for Seniors',
			location: 'Miami',
			topic: 'Digital Literacy',
			text: 'Personalized one-on-one coaching helps older adults learn to use smartphones and tablets to access important services.',
			date: '2023-03-28'
		},
		{
			name: 'Urban Wildlife Corridor',
			location: 'Philadelphia',
			topic: 'Urban Environment',
			text: 'Connected green spaces through the city create safe passage for local wildlife while providing recreational opportunities for residents.',
			date: '2023-05-10'
		},
		{
			name: 'Youth Tech Innovation Lab',
			location: 'Chicago',
			topic: 'Technology Access',
			text: 'After-school program teaches programming and digital fabrication skills to middle school students from underrepresented backgrounds in tech.',
			date: '2023-04-15'
		},
		{
			name: 'Sustainable Ranching Practices',
			location: 'Rural Montana',
			topic: 'Climate Change',
			text: 'Ranchers implemented regenerative grazing methods that sequester carbon while improving soil health and water retention.',
			date: '2023-06-22'
		},
		{
			name: 'Neighborhood Safety Watch',
			location: 'New Orleans',
			topic: 'Community Safety',
			text: 'Resident-organized patrol groups work in partnership with local police to reduce crime through increased visibility and community presence.',
			date: '2023-07-03'
		},
		{
			name: 'Multilingual Support Services',
			location: 'Miami',
			topic: 'Cultural Preservation',
			text: 'Volunteer interpreters ensure non-English speakers can fully participate in community meetings and access local services.',
			date: '2023-03-28'
		},
		{
			name: 'Community Land Trust',
			location: 'Philadelphia',
			topic: 'Housing',
			text: 'Nonprofit acquires land to develop permanently affordable housing, preventing displacement in rapidly gentrifying neighborhoods.',
			date: '2023-05-10'
		},
		{
			name: 'School Garden Initiative',
			location: 'Chicago',
			topic: 'Food Security',
			text: 'Every public school established edible gardens that supply cafeterias with fresh produce while teaching students about nutrition and agriculture.',
			date: '2023-04-15'
		},
		{
			name: 'Rural Energy Efficiency',
			location: 'Rural Montana',
			topic: 'Climate Change',
			text: 'Community-wide weatherization program helped residents reduce energy consumption and lower utility bills during extreme weather seasons.',
			date: '2023-06-22'
		},
		{
			name: 'Healthcare Navigation Team',
			location: 'New Orleans',
			topic: 'Healthcare Access',
			text: 'Trained advocates help residents understand health insurance options and access appropriate care within complex medical systems.',
			date: '2023-07-03'
		},
		{
			name: 'Cultural Heritage Festival',
			location: 'Miami',
			topic: 'Cultural Preservation',
			text: 'Annual celebration showcases traditional music, dance, crafts, and cuisine from the diverse communities represented in the area.',
			date: '2023-03-28'
		},
		{
			name: 'Cooperative Child Care',
			location: 'Philadelphia',
			topic: 'Education',
			text: 'Parents established a rotating child care system, sharing responsibilities and reducing costs while building community connections.',
			date: '2023-05-10'
		},
		{
			name: 'Stormwater Management Project',
			location: 'Chicago',
			topic: 'Urban Environment',
			text: 'Residents installed rain gardens and permeable pavement to reduce flooding and filter pollutants before they reach local waterways.',
			date: '2023-04-15'
		},
		{
			name: 'Rural Digital Skills Training',
			location: 'Rural Montana',
			topic: 'Digital Literacy',
			text: 'Mobile computer lab travels between small towns providing essential digital literacy training for job seekers and small business owners.',
			date: '2023-06-22'
		},
		{
			name: 'Heat Wave Response Network',
			location: 'New Orleans',
			topic: 'Climate Change',
			text: 'Volunteer system identifies vulnerable residents during extreme heat events, ensuring they have access to cooling centers and adequate hydration.',
			date: '2023-07-03'
		},
		{
			name: 'Language Exchange Program',
			location: 'Miami',
			topic: 'Education',
			text: 'Structured conversation groups allow participants to practice new languages while forming cross-cultural friendships and connections.',
			date: '2023-03-28'
		},
		{
			name: 'Shared Mobility Initiative',
			location: 'Philadelphia',
			topic: 'Urban Environment',
			text: 'Community-owned bike and scooter sharing program provides affordable transportation options while reducing car traffic.',
			date: '2023-05-10'
		},
		{
			name: 'Intergenerational Housing Project',
			location: 'Chicago',
			topic: 'Housing',
			text: 'Purpose-built development integrates senior housing with family units, creating natural opportunities for support and connection across generations.',
			date: '2023-04-15'
		},
		{
			name: 'Mental Health First Aid',
			location: 'Rural Montana',
			topic: 'Healthcare Access',
			text: 'Training program equips community members to recognize and respond appropriately to mental health crises until professional help is available.',
			date: '2023-06-22'
		},
		{
			name: 'Coastal Restoration Volunteers',
			location: 'New Orleans',
			topic: 'Climate Change',
			text: 'Regular community workdays restore wetlands and plant native species to improve natural storm protection for vulnerable coastlines.',
			date: '2023-07-03'
		},
		{
			name: 'Public Art Restoration',
			location: 'Miami',
			topic: 'Cultural Preservation',
			text: 'Community effort to preserve and restore historic murals and sculptures that represent important moments in neighborhood history.',
			date: '2023-03-28'
		},
		{
			name: 'Community Solar Project',
			location: 'Philadelphia',
			topic: 'Climate Change',
			text: 'Residents without suitable rooftops invest in shared solar installation, receiving energy credits while supporting renewable power generation.',
			date: '2023-05-10'
		},
		{
			name: 'Night Market Initiative',
			location: 'Chicago',
			topic: 'Food Security',
			text: 'Monthly evening markets feature local food entrepreneurs, increasing access to culturally appropriate foods and supporting small businesses.',
			date: '2023-04-15'
		},
		{
			name: 'Rural Healthcare Innovation',
			location: 'Rural Montana',
			topic: 'Healthcare Access',
			text: 'Telemedicine program connects local clinics with specialists at urban medical centers, providing comprehensive care without extensive travel.',
			date: '2023-06-22'
		}
	];

	return { stories, params };
}
