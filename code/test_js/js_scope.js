var jQuery = 'I\'m not jQuery.';
var global_variable = 'global!';
(function ($, test) { console.log($);
                    console.log(test)})(jQuery, global_variable);