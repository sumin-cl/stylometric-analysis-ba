import re
import html

import re
import html

def clean_reddit_text(text):
    """
    Reinigt Reddit-Posts für stylometrische Analyse.
    """
    if not isinstance(text, str):
        return ""

    # 1. Double Unescape
    text = html.unescape(html.unescape(text))

    # 2. Reddit-Specific Garbage
    text = text.replace('&#x200B;', '').replace('\u200b', '')
    text = re.sub(r'\*Processing img \S+\.\.\.\*', '', text)

    # 3. Code-Blöcke (```...```)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    
    # 4. Inline Code (`...`)
    text = re.sub(r'`[^`]+`', '', text)

    # 5. Markdown-Links [Text](URL) -> Text
    text = re.sub(r'\[([^\]]*)\]\([^\)]+\)', r' \1 ', text)
    # [1]: oder [^1]: (Footnote-Referenzen)
    text = re.sub(r'\[\^?\d+\]:?', '', text)
    # Entfernt übrig gebliebene [ ... ] oder [ ... ] (oft bei Zitaten)
    text = re.sub(r'\[\s*\.*\s*\]', '', text)

    # 6. Verbliebene URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    # 7. GARBAGE COLLECTOR
    # Backslashes (oft vor Leerzeichen oder Klammern: \ )
    text = text.replace('\\', '')
    # Doppel-Anführungszeichen-Artefakte (""Wort"") -> "Wort"
    text = text.replace('""', '"')
    # Header (#), Bold/Italic (* oder _), Listen-Marker (-)
    text = re.sub(r'[#*_>\-]{1,}', ' ', text)
    
    # 8. Whitespace normalisieren
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# --- TEST-BEREICH ---
if __name__ == "__main__":
    sample_post = """
    "I have been playing around with some LSTM models in R over the past few days from various tutorials. However the tutorials I have been using all break in their code at some point so I can not get a decent model to work from start to finish.

    I have followed[this](http://rwanjohi.rbind.io/2018/04/05/time-series-forecasting-using-lstm-in-r/) tutorial but they seem to stop and not show the code for the final graph. [This](https://stackoverflow.com/questions/52292452/lstm-understanding-possible-overfit) SO post was also quite useful in understanding that tutorial.

    [This](https://www.business-science.io/timeseries-analysis/2018/04/18/keras-lstm-sunspots-time-series-prediction.html) tutorial seems to be very promising but it breaks.

    Heres my cut down version of it if anybody can help me solve the issue I am having (in regards to the map\_dbl())

    [This](https://statkclee.github.io/model/model-rsampling-time-series.html) tutorial uses the same code as ""tutorial 3"" here but on a different dataset.

    &amp;#x200B;

    `# Core Tidyverse`

    `library(tidyverse)`

    `library(glue)`

    `library(forcats)`

    &amp;#x200B;

    `# Time Series`

    `library(timetk)`

    `library(tidyquant)`

    `library(tibbletime)`

    &amp;#x200B;

    `# Visualization`

    `library(cowplot)`

    &amp;#x200B;

    `# Preprocessing`

    `library(recipes)`

    &amp;#x200B;

    `# Sampling / Accuracy`

    `library(rsample)`

    `library(yardstick)` 

    &amp;#x200B;

    `# Modeling`

    `library(keras)`

    &amp;#x200B;

    `sun_spots &lt;- datasets::sunspot.month %&gt;%`

    `tk_tbl() %&gt;%`

    `mutate(index = as_date(index)) %&gt;%`

    `as_tbl_time(index = index)`

    &amp;#x200B;

    `sun_spots`

    `############################################`

    &amp;#x200B;

    `periods_train &lt;- 12 * 50`

    `periods_test  &lt;- 12 * 10`

    `skip_span     &lt;- 12 * 20`

    &amp;#x200B;

    `rolling_origin_resamples &lt;- rolling_origin(`

    `sun_spots,`

    `initial    = periods_train,`

    `assess     = periods_test,`

    `cumulative = FALSE,`

    `skip       = skip_span`

    `)`

    &amp;#x200B;

    `rolling_origin_resamples`

    &amp;#x200B;

    `############################################`

    &amp;#x200B;

    `calc_rmse &lt;- function(prediction_tbl) {`

    

    `rmse_calculation &lt;- function(data) {`

    `data %&gt;%`

    `spread(key = key, value = value) %&gt;%`

    `select(-index) %&gt;%`

    `filter(!`[`is.na`](https://is.na)`(predict)) %&gt;%`

    `rename(`

    `truth    = actual,`

    `estimate = predict`

    `) %&gt;%`

    `rmse(truth, estimate)`

    `}`

    

    `safe_rmse &lt;- possibly(rmse_calculation, otherwise = NA)`

    

    `safe_rmse(prediction_tbl)`

    

    `}`

    &amp;#x200B;

    `#############################################`

    &amp;#x200B;

    `predict_keras_lstm &lt;- function(split, epochs = 300, ...) {`

    

    `lstm_prediction &lt;- function(split, epochs, ...) {`



    `# 5.1.2 Data Setup`

    `df_trn &lt;- training(split)`

    `df_tst &lt;- testing(split)`



    `df &lt;- bind_rows(`

    `df_trn %&gt;% add_column(key = ""training""),`

    `df_tst %&gt;% add_column(key = ""testing"")`

    `) %&gt;%` 

    `as_tbl_time(index = index)`



    `# 5.1.3 Preprocessing`

    `rec_obj &lt;- recipe(value ~ ., df) %&gt;%`

    `step_sqrt(value) %&gt;%`

    `step_center(value) %&gt;%`

    `step_scale(value) %&gt;%`

    `prep()`



    `df_processed_tbl &lt;- bake(rec_obj, df)`



    `center_history &lt;- rec_obj$steps[[2]]$means[""value""]`

    `scale_history  &lt;- rec_obj$steps[[3]]$sds[""value""]`



    `# 5.1.4 LSTM Plan`

    `lag_setting  &lt;- 120 # = nrow(df_tst)`

    `batch_size   &lt;- 40`

    `train_length &lt;- 440`

    `tsteps       &lt;- 1`

    `epochs       &lt;- epochs`



    `# 5.1.5 Train/Test Setup`

    `lag_train_tbl &lt;- df_processed_tbl %&gt;%`

    `mutate(value_lag = lag(value, n = lag_setting)) %&gt;%`

    `filter(!`[`is.na`](https://is.na)`(value_lag)) %&gt;%`

    `filter(key == ""training"") %&gt;%`

    `tail(train_length)`



    `x_train_vec &lt;- lag_train_tbl$value_lag`

    `x_train_arr &lt;- array(data = x_train_vec, dim = c(length(x_train_vec), 1, 1))`



    `y_train_vec &lt;- lag_train_tbl$value`

    `y_train_arr &lt;- array(data = y_train_vec, dim = c(length(y_train_vec), 1))`



    `lag_test_tbl &lt;- df_processed_tbl %&gt;%`

    `mutate(`

    `value_lag = lag(value, n = lag_setting)`

    `) %&gt;%`

    `filter(!`[`is.na`](https://is.na)`(value_lag)) %&gt;%`

    `filter(key == ""testing"")`



    `x_test_vec &lt;- lag_test_tbl$value_lag`

    `x_test_arr &lt;- array(data = x_test_vec, dim = c(length(x_test_vec), 1, 1))`



    `y_test_vec &lt;- lag_test_tbl$value`

    `y_test_arr &lt;- array(data = y_test_vec, dim = c(length(y_test_vec), 1))`



    `# 5.1.6 LSTM Model`

    `model &lt;- keras_model_sequential()`



    `model %&gt;%`

    `layer_lstm(units            = 50,` 

    `input_shape      = c(tsteps, 1),` 

    `batch_size       = batch_size,`

    `return_sequences = TRUE,` 

    `stateful         = TRUE) %&gt;%` 

    `layer_lstm(units            = 50,` 

    `return_sequences = FALSE,` 

    `stateful         = TRUE) %&gt;%` 

    `layer_dense(units = 1)`



    `model %&gt;%` 

    `compile(loss = 'mae', optimizer = 'adam')`



    `# 5.1.7 Fitting LSTM`

    `for (i in 1:epochs) {`

    `model %&gt;% fit(x          = x_train_arr,` 

    `y          = y_train_arr,` 

    `batch_size = batch_size,`

    `epochs     = 1,` 

    `verbose    = 1,` 

    `shuffle    = FALSE)`



    `model %&gt;% reset_states()`

    `cat(""Epoch: "", i)`



    `}`



    `# 5.1.8 Predict and Return Tidy Data`

    `# Make Predictions`

    `pred_out &lt;- model %&gt;%` 

    `predict(x_test_arr, batch_size = batch_size) %&gt;%`

    `.[,1]` 



    `# Retransform values`

    `pred_tbl &lt;- tibble(`

    `index   = lag_test_tbl$index,`

    `value   = (pred_out * scale_history + center_history)^2`

    `)` 



    `# Combine actual data with predictions`

    `tbl_1 &lt;- df_trn %&gt;%`

    `add_column(key = ""actual"")`



    `tbl_2 &lt;- df_tst %&gt;%`

    `add_column(key = ""actual"")`



    `tbl_3 &lt;- pred_tbl %&gt;%`

    `add_column(key = ""predict"")`



    `# Create time_bind_rows() to solve dplyr issue`

    `time_bind_rows &lt;- function(data_1, data_2, index) {`

    `index_expr &lt;- enquo(index)`

    `bind_rows(data_1, data_2) %&gt;%`

    `as_tbl_time(index = !! index_expr)`

    `}`



    `ret &lt;- list(tbl_1, tbl_2, tbl_3) %&gt;%`

    `reduce(time_bind_rows, index = index) %&gt;%`

    `arrange(key, index) %&gt;%`

    `mutate(key = as_factor(key))`



    `return(ret)`



    `}`

    

    `safe_lstm &lt;- possibly(lstm_prediction, otherwise = NA)`

    

    `safe_lstm(split, epochs, ...)`

    

    `}`

    &amp;#x200B;

    `#################################################`

    &amp;#x200B;

    `sample_predictions_lstm_tbl &lt;- rolling_origin_resamples %&gt;%`

    `mutate(predict = map(splits, predict_keras_lstm, epochs = 10))`

    &amp;#x200B;

    `sample_predictions_lstm_tbl`

    &amp;#x200B;

    &amp;#x200B;

    `sample_predictions_lstm_tbl$predict`

    `map_dbl(sample_predictions_lstm_tbl$predict, calc_rmse)`

    &amp;#x200B;

    `sample_rmse_tbl &lt;- sample_predictions_lstm_tbl %&gt;%`

    `mutate(rmse = map_dbl(predict, calc_rmse)) %&gt;%`

    `select(id, rmse)`"
    """
    
    print("ORIGINAL:")
    print(sample_post)
    print("-" * 20)
    print("CLEAN:")
    print(clean_reddit_text(sample_post))