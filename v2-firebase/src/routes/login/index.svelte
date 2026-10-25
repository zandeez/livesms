<script>
	import { signInWithPopup, GoogleAuthProvider, onAuthStateChanged, signInWithEmailAndPassword } from 'firebase/auth';
	import { auth } from '$lib/firebase';
	import { onDestroy } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	let email = '';
	let password = '';
	let loginError = null;

	onDestroy(onAuthStateChanged(auth, (user) => {
		if (user) {
			if ($page.query.has('next')) {
				goto(decodeURI($page.query.get('next')));
			} else {
				goto('/');
			}
		}
	}));

	function loginGoogle() {
		signInWithPopup(auth, new GoogleAuthProvider());
	}

	function loginEmail() {
		signInWithEmailAndPassword(auth, email, password);
	}

	$: valid = !(email && email.length > 0 && password && password.length > 0);
</script>

<svelte:head>
	<title>LiveSMS - Login</title>
</svelte:head>

<div id='container'>
	<div id='window'>
		<h1>LiveSMS Login</h1>
		{#if loginError}
			<div class='alert danger'>
				{ loginError }
			</div>
		{/if}
		<form>
			<div class='mb-4'>
				<label class='block mb-2' for='email'>Email</label>
				<input
					id='email'
					name='email'
					placeholder='Email'
					bind:value={email}
					:disabled='loginCancel'
				/>
			</div>
			<div class='mb-4'>
				<label class='block mb-2' for='password'>Password</label>
				<input
					id='password'
					name='password'
					placeholder='Password'
					type='password'
					bind:value={password}
					:disabled='loginCancel'
				/>
			</div>
			<button type='button' disabled={valid}>Login</button>
			<button class="google" on:click={loginGoogle} type="button"></button>
		</form>
	</div>
</div>

<style>
    .google {
        @apply h-16 bg-transparent bg-center bg-contain bg-no-repeat;
        background-image: url("/btn_google_signin_dark_normal_web@2x.png");
    }

    .google:hover {
        background-image: url("/btn_google_signin_dark_focus_web@2x.png");
    }

    .google:active {
        background-image: url("/btn_google_signin_dark_pressed_web@2x.png");
    }

    .google:disabled {
        background-image: url("/btn_google_signin_dark_disabled_web@2x.png");
    }

    #container {
        @apply flex content-center justify-center mx-auto h-screen items-center flex-col;
    }

    #window {
        @apply border-2 border-gray-200 bg-white p-8 rounded shadow-lg;
    }

    #window h1 {
        @apply my-0 text-center;
    }

    form {
        @apply mt-4;
    }
</style>
