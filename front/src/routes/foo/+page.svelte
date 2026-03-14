<div class="cards-container">
    <div class="card">
        <input type="checkbox" id="card1" class="card-toggle" />
        <label for="card1" class="card-header">Card one</label>
        <div class="card-body">
            <div class="card-inner">
                <p>
                    Content for the first card. It can be as long as you like.
                    When collapsed, only the header is visible at a minimum
                    height; click to expand and see this content with a smooth
                    height animation.
                </p>
            </div>
        </div>
    </div>

    <div class="card">
        <input type="checkbox" id="card2" class="card-toggle" />
        <label for="card2" class="card-header">Card two</label>
        <div class="card-body">
            <div class="card-inner">
                <p>
                    Second card body. Also expandable and collapsible. Pure CSS,
                    no JavaScript.
                </p>
            </div>
        </div>
    </div>

    <div class="card">
        <input type="checkbox" id="card3" class="card-toggle" />
        <label for="card3" class="card-header">Card three</label>
        <div class="card-body">
            <div class="card-inner">
                <p>
                    Third card with more content to show the animation clearly
                    when expanding and collapsingThird card with more content to
                    show the animation clearly when expanding and
                    collapsingThird card with more content to show the animation
                    clearly when expanding and collapsingThird card with more
                    content to show the animation clearly when expanding and
                    collapsingThird card with more content to show the animation
                    clearly when expanding and collapsingThird card with more
                    content to show the animation clearly when expanding and
                    collapsingThird card with more content to show the animation
                    clearly when expanding and collapsingThird card with more
                    content to show the animation clearly when expanding and
                    collapsingThird card with more content to show the animation
                    clearly when expanding and collapsingThird card with more
                    content to show the animation clearly when expanding and
                    collapsingThird card with more content to show the animation
                    clearly when expanding and collapsingThird card with more
                    content to show the animation clearly when expanding and
                    collapsingThird card with more content to show the animation
                    clearly when expanding and collapsingThird card with more
                    content to show the animation clearly when expanding and
                    collapsingThird card with more content to show the animation
                    clearly when expanding and collapsingThird card with more
                    content to show the animation clearly when expanding and
                    collapsingThird card with more content to show the animation
                    clearly when expanding and collapsingThird card with more
                    content to show the animation clearly when expanding and
                    collapsingThird card with more content to show the animation
                    clearly when expanding and collapsingThird card with more
                    content to show the animation clearly when expanding and
                    collapsingThird card with more content to show the animation
                    clearly when expanding and collapsingThird card with more
                    content to show the animation clearly when expanding and
                    collapsing.
                </p>
            </div>
        </div>
    </div>
</div>

<style>
    * {
        color: black;
    }
    .cards-container {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        width: 32rem;
        max-width: 100%;
        margin: 0 auto;
        padding: 1rem;
        box-sizing: border-box;
    }

    .card {
        border: 1px solid #ccc;
        border-radius: 8px;
        overflow: hidden;
        background: #fff;
        width: 100%;
        min-width: 0;
        box-sizing: border-box;
    }

    .card-toggle {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip-path: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }

    .card-header {
        min-height: 3rem;
        padding: 0.75rem 1rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        font-weight: 600;
        background: #f5f5f5;
        transition: background 0.2s ease;
    }

    .card-header::before {
        content: "▶";
        margin-right: 0.5rem;
        font-size: 0.75rem;
        transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .card-toggle:checked ~ .card-header::before {
        transform: rotate(90deg);
    }

    .card-header:hover {
        background: #eee;
    }

    .card-body {
        display: grid;
        grid-template-rows: 0fr;
        transition: grid-template-rows 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .card-toggle:checked ~ .card-body {
        grid-template-rows: 1fr;
    }

    .card-inner {
        min-height: 0;
        overflow: hidden;
        min-width: 0;
    }

    .card-inner p {
        margin: 0;
        padding: 1rem;
        border-top: 1px solid #eee;
        overflow-wrap: break-word;
    }
</style>
