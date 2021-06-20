const gulp = require("gulp")

const css = () => {
    const postCSS = require("gulp-postcss");
    const sass = require("gulp-sass");
    const minify = require("gulp-csso");
    sass.compiler = require("node-sass");
    return gulp
    .src("assets/scss/styles.scss") //일반적인 scss 를css 로 바꿔줌
    .pipe(sass().on("error",sass.logError))
    .pipe(postCSS([
        require("tailwindcss"),
        require("autoprefixer")
    ])) //실제 css 로 바꿈 구글 크롬은 이런것들 이해 못해서
    .pipe(minify()) //코드를 짦게 만듬
    .pipe(gulp.dest("static/css")); //결과를 static css 로 보냄냄
       //브라우저에 보내는건 static/css/styles.css
};
exports.default = css;

//암튼 sas 를 css 로 바꿔서
//수정은 반드시 scss 에서 수정
//scss 변경할시 npm run css 해야함!