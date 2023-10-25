document.addEventListener('DOMContentLoaded', function() {
    document.getElementById("delete-button").addEventListener("click", function() {
    if (confirm("Are you sure you want to delete this balance?(This is irreversible.)")) {
        // If the user clicks "OK" in the confirmation popup, proceed with the redirect
        window.location.href = "./delete";
    } else {
        // If the user clicks "Cancel" in the confirmation popup, do nothing
    }
    })
});