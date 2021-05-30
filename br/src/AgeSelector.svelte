<script>
    export let age = 0;
</script>

<style>
	div.age_selector-overlay {
		position: absolute;
		z-index: 999;
		top: 1.2em;
		left: 4em;
		backdrop-filter: saturate(100%) blur(5px);
		background-color: rgba(255, 255, 255, .90);
	}
</style>

<div class="btn-group age_selector-overlay" role="group" aria-label="Age band selector">
  <input type="radio" class="btn-check" name="age" id="under_1" value={0} bind:group={age} autocomplete="off">
  <label class="btn btn-lg btn-outline-primary" for="under_1">Under 1</label>

  <input type="radio" class="btn-check" name="age" id="under_5" value={1} bind:group={age} autocomplete="off">
  <label class="btn btn-lg btn-outline-primary" for="under_5">Under 5</label>
</div>