var form = document.getElementById('quizform')
form.onsubmit =
    function () {
        let val = document.getElementById('inputCategory').value
        if (val === 'null') {
            alert("Choose any category :(")
            return false
        }
    }

