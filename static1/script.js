const search = document.getElementById("search");

if (search) {

    search.addEventListener("keyup", function () {

        fetch("/search?q=" + search.value)

            .then(response => response.json())

            .then(data => {

                const list =
                    document.getElementById("searchResults");

                list.innerHTML = "";

                data.forEach(note => {

                    list.innerHTML +=
                        `<li>${note.title}</li>`;

                });

            });

    });

}