<script>
    import { createEventDispatcher } from 'svelte';
    let year = '2021';
    let month = '';
    const dispatch = createEventDispatcher();

    function onchangeYear() {
        month = '';
        dispatch('message', {
            year: year,
            month: month
        });
    };
    
    function onchangeMonth() {
        dispatch('message', {
            year: year,
            month: month
        });
    };
</script>

<style>
	div.date-selector-overlay {
		position: absolute;
		z-index: 999;
		top: 1.2em;
        left: 37.5%;
        width: 25%;
	}
</style>

<div class="date-selector-overlay">
    <div class="input-group">
        <select class="form-select form-select-lg mb-3" bind:value={year} on:change|self={onchangeYear}>
            <option value="2021" selected>2021</option>
            <option value="2020">2020</option>
            <option value="2019">2019</option>
            <option value="2018">2018</option>
            <option value="2017">2017</option>
            <option value="2016">2016</option>
            <option value="2015">2015</option>
            <option value="2014">2014</option>
            <option value="2013">2013</option>
            <option value="2012">2012</option>
            <option value="2011">2011</option>
        </select>
        <select class="form-select form-select-lg mb-3" bind:value={month} on:change|self={onchangeMonth}>
            <option value="" selected>Month</option>
            <option value="1">January</option>
            <option value="2">February</option>
            <option value="3">March</option>
            <option value="4">April</option>
            <option value="5">May</option>
            <option value="6">June</option>
            <option value="7">July</option>
            <option value="8">August</option>
            <option value="9">September</option>
            <option value="10">October</option>
            <option value="11">November</option>
            <option value="12">December</option>
        </select>
    </div>
</div>