// Verwijdert een project via de server en laadt daarna een andere pagina.
function deleteProject(projectId){
	fetch("/delete-project", {
		method: "POST",
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({projectId: projectId}),
	} ).then((_res) => {
		window.location.href = "/mijn_projecten"
	}
	);
}

