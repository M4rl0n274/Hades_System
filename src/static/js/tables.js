document.addEventListener("DOMContentLoaded", () => {
    const sortSelect = document.getElementById("sortSelect");
    const tableBody = document.getElementById("table-body");

    if (!sortSelect || !tableBody) return;

    // Guarda el orden original de las filas
    const originalRows = Array.from(tableBody.querySelectorAll("tr"));

    sortSelect.addEventListener("change", (e) => {
        const value = e.target.value;
        if (value === "default") {
            // Restaura la tabla enviada por Jinja2
            tableBody.innerHTML = "";
            originalRows.forEach(row => tableBody.appendChild(row));
            return;
        }

        const [column, direction] = value.split("-");
        const rows = Array.from(tableBody.querySelectorAll("tr:not(.empty-row)"));

        // Mapeo del índice de columnas para ordenar
        const columnIndexMap = {
            "id": 0,
            "nombre": 1,
            "apellido": 2
        };

        const index = columnIndexMap[column];
        if (index === undefined) return;

        rows.sort((rowA, rowB) => {
            let cellA = rowA.children[index].textContent.trim();
            let cellB = rowB.children[index].textContent.trim();

            // Si es ID o número, convierte a Integer para orden numérico correcto
            if (column === "id") {
                cellA = parseInt(cellA, 10) || 0;
                cellB = parseInt(cellB, 10) || 0;
                return direction === "asc" ? cellA - cellB : cellB - cellA;
            }

            // Ordenamiento alfabético para texto
            return direction === "asc" 
                ? cellA.localeCompare(cellB, 'es', { sensitivity: 'base' })
                : cellB.localeCompare(cellA, 'es', { sensitivity: 'base' });
        });

        // Reinserta las filas ordenadas en el DOM
        tableBody.innerHTML = "";
        rows.forEach(row => tableBody.appendChild(row));
    });
});