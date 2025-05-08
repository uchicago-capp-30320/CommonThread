<script>
	let {
		ageFilter = 'all',
		genderFilter = 'all',
		stateFilter = 'all',
		educationFilter = 'all',
		onFilterChange = () => {}
	} = $props();
</script>

<div class="sidebar">
	<h3>Filter by</h3>
	<hr />

	<div class="filter-section">
		<h4>AGE</h4>
		<div class="filter-options">
			<select
				bind:value={ageFilter}
				onchange={() => onFilterChange('age', ageFilter)}
				class="filter-dropdown"
			>
				<option value="all">All</option>
				<option value="21-29">21-29</option>
				<option value="30-39">30-39</option>
				<option value="40-49">40-49</option>
				<option value="50-59">50-59</option>
				<option value="60-69">60-69</option>
				<option value="70-79">70-79</option>
			</select>
		</div>
	</div>

	<div class="filter-section">
		<h4>GENDER</h4>
		<div class="filter-options">
			<button
				class={genderFilter === 'all' ? 'filter-btn active' : 'filter-btn'}
				onclick={() => onFilterChange('gender', 'all')}
			>
				All
			</button>
			<button
				class={genderFilter === 'Male' ? 'filter-btn active' : 'filter-btn'}
				onclick={() => onFilterChange('gender', 'Male')}
			>
				Male
			</button>
			<button
				class={genderFilter === 'Female' ? 'filter-btn active' : 'filter-btn'}
				onclick={() => onFilterChange('gender', 'Female')}
			>
				Female
			</button>
			<button
				class={genderFilter === 'Non-binary' ? 'filter-btn active' : 'filter-btn'}
				onclick={() => onFilterChange('gender', 'Non-binary')}
			>
				Non-binary
			</button>
		</div>
	</div>

	<div class="filter-section">
		<h4>EDUCATION</h4>
		<div class="filter-options">
			<button
				class={educationFilter === 'all' ? 'filter-btn active' : 'filter-btn'}
				onclick={() => onFilterChange('education', 'all')}
			>
				All
			</button>
			<button
				class={educationFilter === 'High School' ? 'filter-btn active' : 'filter-btn'}
				onclick={() => onFilterChange('education', 'High School')}
			>
				High School
			</button>
			<button
				class={educationFilter === 'Some College' ? 'filter-btn active' : 'filter-btn'}
				onclick={() => onFilterChange('education', 'Some College')}
			>
				Some College
			</button>
			<button
				class={educationFilter === 'Associate Degree' ? 'filter-btn active' : 'filter-btn'}
				onclick={() => onFilterChange('education', 'Associate Degree')}
			>
				Associate Degree
			</button>
			<button
				class={educationFilter === 'Bachelors Degree' ? 'filter-btn active' : 'filter-btn'}
				onclick={() => onFilterChange('education', 'Bachelors Degree')}
			>
				Bachelors Degree
			</button>
			<button
				class={educationFilter === 'Masters Degree' ? 'filter-btn active' : 'filter-btn'}
				onclick={() => onFilterChange('education', 'Masters Degree')}
			>
				Masters Degree
			</button>
			<button
				class={educationFilter === 'Doctorate' ? 'filter-btn active' : 'filter-btn'}
				onclick={() => onFilterChange('education', 'Doctorate')}
			>
				Doctorate
			</button>
		</div>
	</div>
	<div class="filter-section">
		<h4>STATE</h4>
		<div class="filter-options">
			<select
				bind:value={stateFilter}
				onchange={() => onFilterChange('state', stateFilter)}
				class="filter-dropdown"
			>
				<option value="all">All</option>
				<option value="AL">AL</option>
				<option value="AK">AK</option>
				<option value="AZ">AZ</option>
				<option value="AR">AR</option>
				<option value="CA">CA</option>
				<option value="CO">CO</option>
				<option value="CT">CT</option>
				<option value="DE">DE</option>
				<option value="FL">FL</option>
				<option value="GA">GA</option>
				<option value="HI">HI</option>
				<option value="ID">ID</option>
				<option value="IL">IL</option>
				<option value="IN">IN</option>
				<option value="IA">IA</option>
				<option value="KS">KS</option>
				<option value="KY">KY</option>
				<option value="LA">LA</option>
				<option value="ME">ME</option>
				<option value="MD">MD</option>
				<option value="MA">MA</option>
				<option value="MI">MI</option>
				<option value="MN">MN</option>
				<option value="MS">MS</option>
				<option value="MO">MO</option>
				<option value="MT">MT</option>
				<option value="NE">NE</option>
				<option value="NV">NV</option>
				<option value="NH">NH</option>
				<option value="NJ">NJ</option>
				<option value="NM">NM</option>
				<option value="NY">NY</option>
				<option value="NC">NC</option>
				<option value="ND">ND</option>
				<option value="OH">OH</option>
				<option value="OK">OK</option>
				<option value="OR">OR</option>
				<option value="PA">PA</option>
				<option value="RI">RI</option>
				<option value="SC">SC</option>
				<option value="SD">SD</option>
				<option value="TN">TN</option>
				<option value="TX">TX</option>
				<option value="UT">UT</option>
				<option value="VT">VT</option>
				<option value="VA">VA</option>
				<option value="WA">WA</option>
				<option value="WV">WV</option>
				<option value="WI">WI</option>
				<option value="WY">WY</option>
			</select>
		</div>
	</div>
</div>

<style>
	.sidebar {
		background-color: #56bcb374;
		padding: 1rem;
		border-radius: 8px;
		height: 100%;
		height: fit-content;
	}

	h3 {
		font-weight: 400;
		margin-top: 0;
		margin-bottom: 0;
		font-size: 1.5rem;
		color: black !important;
	}

	h4 {
		margin: 1rem 0 0.5rem;
		font-size: 0.8rem;
		color: black !important;
	}

	.filter-options {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.filter-btn {
		background-color: #e0e0e0;
		border: none;
		padding: 0.5rem;
		border-radius: 4px;
		cursor: pointer;
		text-align: left;
		font-size: 0.9rem;
	}

	.filter-btn.active {
		background-color: var(--dark-blue);
		color: white;
	}
</style>
