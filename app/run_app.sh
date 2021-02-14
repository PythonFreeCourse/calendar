uvicorn app.main:app --reload
pytest -vvv --junitxml=junit/test-results.xml --cov-report=xml --cov=app ./tests --cov-report html --cov-report term-missing
flake8 app ./tests --count --show-source --statistics
flake8 app ./tests --count --exit-zero --max-complexity=10 --statistics

<!--<div>-->
<!--    <form name="Form" onsubmit="return validateForm({{ events }})">-->
<!--        <div class="form-row align-items-center">-->
<!--            <div class="col-sm-2 my-1">-->
<!--                <label for="category" class="sr-only">Filter events by category </label>-->
<!--                <input type="text" id="category" name="category"-->
<!--                       class="form-control" placeholder="category"-->
<!--                       value="{{ category }}" onfocus="this.value=''" required>-->
<!--                <input onchange="validateForm({{ events }});" onkeypress="this.onchange();" oninput="this.onchange();">-->
<!--            </div>-->
<!--            <div class="col my-1">-->
<!--                <input type="submit" class="btn btn-primary" value="Filter">-->
<!--            </div>-->
<!--        </div>-->
<!--    </form>-->

<!--    <span onclick='validateForm()'>Click me!</span>-->
<!--    <button onclick='validateForm()' >Click me</button>-->
<!--    <p>-->
<!--        {{ events.values() }}-->
<!--    </p>-->
<!--</div>-->

<!--    <div>{{ events_list | selectattr('category_id', 'equalto', 1) | list }}</div>-->
<!--    <div>{{ events_list | rejectattr('category_id', 'equalto', 1) | list }}</div>-->
<!--    <div>&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;</div>-->
<!--    <div>{{ events_list | pprint }}</div>-->
<!--    <div>&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;</div>-->
<!--        {% set events_list = events_list | selectattr('category_id', 'equalto', 1) | list %}-->


<!--            {% if event | attr("category_id") == '1' %}-->
<!--                <div>Event - {{ event}}</div>-->
<!--            {% endif %}-->

<!--    <script type="text/javascript">-->
<!--        console.log(event);-->
<!--        console.log(typeof(event));-->
<!--    </script>-->



<!--<script type="text/javascript">-->
<!--    function validateForm() {-->
<!--        const text = "{{ events }}";-->
<!--        console.log(text);-->
<!--        console.log(Object.values('{{events}}'));-->
<!--        console.log(Object.values(text));-->
<!--        console.log(events.values);-->
<!--        var newArray = events.values.filter(function (el) {-->
<!--            return el[0].category_id === 1;-->
<!--        });-->
<!--        console.log(newArray);-->
<!--        return newArray;-->
<!--    }-->
<!--</script>-->