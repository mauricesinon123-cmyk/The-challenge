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
