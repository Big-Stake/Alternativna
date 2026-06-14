function changeStatus(id) {

    fetch("/change_status/" + id, {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {

        document.getElementById(
            "status-" + id
        ).innerText = data.status;

    });

}