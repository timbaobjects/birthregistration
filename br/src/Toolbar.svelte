<script>
	export let exportHandler = () => {};
</script>

<style>
	div.toolbar-overlay {
		position: absolute;
		z-index: 999;
		top: 24.2px;
		right: 10px;
		backdrop-filter: saturate(100%) blur(5px);
		background-color: rgba(255, 255, 255, .90);
	}
</style>

<div class="toolbar-overlay">
	<a href="/br/old/" class="btn btn-md btn-dark">Reporting Dashboard</a>
	<a href="https://staging.rapidsmsnigeria.org/br" class="btn btn-md btn-primary">Coverage</a>
    <button class="btn btn-md btn-primary" on:click="{exportHandler}">
        Export
    </button>
</div>