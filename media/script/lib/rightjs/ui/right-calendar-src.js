/**
 * The calendar widget implemented with RightJS
 *
 * Home page: http://rightjs.org/ui/calendar
 *
 * @copyright (C) 2009 Nikolay V. Nemshilov aka St.
 */
if (!RightJS) { throw "Gimme RightJS. Please." };

/**
 * The calendar widget for RightJS
 *
 *
 * Copyright (C) 2009 Nikolay V. Nemshilov aka St.
 */
var Calendar = new Class(Observer, {
  extend: {
    EVENTS: $w('show hide select done'),
    
    Options: {
      format:         'ISO', // a key out of the predefined formats or a format string
      showTime:       false,
      showButtons:    false,
      minDate:        null,
      maxDate:        null,
      firstDay:       1,     // 1 for Monday, 0 for Sunday
      fxDuration:     200,
      numberOfMonths: 1,     // a number or [x, y] greed definition
      timePeriod:     1,     // the timepicker minimal periods (in minutes, might be bigger than 60)
      checkTags:      '*',
      relName:        'calendar'
    },
    
    Formats: {
      ISO:    '%Y-%m-%d',
      POSIX:  '%Y/%m/%d',
      EUR:    '%d-%m-%Y',
      US:     '%m/%d/%Y'
    },
    
    i18n: {
      Done:  'Done',
      Now:   'Now',
      Next:  'Next Month',
      Prev:  'Previous Month',
      
      dayNames:        $w('Sunday Monday Tuesday Wednesday Thursday Friday Saturday'),
      dayNamesShort:   $w('Sun Mon Tue Wed Thu Fri Sat'),
      dayNamesMin:     $w('Su Mo Tu We Th Fr Sa'),
      monthNames:      $w('January February March April May June July August September October November December'),
      monthNamesShort: $w('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec')
    }
  },
  
  /**
   * Basic constructor
   *
   * @param Object options
   */
  initialize: function(options) {
    this.$super(options);
    
    this.element = $E('div', {'class': 'right-calendar'});
    this.build().connectEvents().setDate(new Date());
  },
  
  /**
   * additional options processing
   *
   * @param Object options
   * @return Calendar this
   */
  setOptions: function(options) {
    this.$super(options);
    
    // merging the i18n tables
    this.options.i18n = {};
    for (var key in this.constructor.i18n) {
      this.options.i18n[key] = isArray(this.constructor.i18n[key]) ? this.constructor.i18n[key].clone() : this.constructor.i18n[key];
    }
    this.options.i18n = Object.merge(this.options.i18n, options||{});
    
    // defining the current days sequence
    this.options.dayNames = this.options.i18n.dayNamesMin;
    if (this.options.firstDay) {
      this.options.dayNames.push(this.options.dayNames.shift());
    }
    
    // the monthes table cleaning up
    if (!isArray(this.options.numberOfMonths)) {
      this.options.numberOfMonths = [this.options.numberOfMonths, 1];
    }
    
    // min/max dates preprocessing
    if (this.options.minDate) this.options.minDate = this.parse(this.options.minDate);
    if (this.options.maxDate) {
      this.options.maxDate = this.parse(this.options.maxDate);
      this.options.maxDate.setDate(this.options.maxDate.getDate() + 1);
    }
    
    // format catching up
    this.options.format = (this.constructor.Formats[this.options.format] || this.options.format).trim();
    
    return this;
  },
  
  /**
   * Sets the date on the calendar
   *
   * @param Date date or String date
   * @return Calendar this
   */
  setDate: function(date) {
    this.date = this.prevDate = this.parse(date);
    return this.update();
  },
  
  /**
   * Returns the current date on the calendar
   *
   * @return Date currently selected date on the calendar
   */
  getDate: function() {
    return this.date;
  },
  
  /**
   * Hides the calendar
   *
   * @return Calendar this
   */
  hide: function() {
    this.element.hide('fade', {duration: this.options.fxDuration});
    return this;
  },
  
  /**
   * Shows the calendar
   *
   * @param Object {x,y} optional position
   * @return Calendar this
   */
  show: function(position) {
    this.element.show('fade', {duration: this.options.fxDuration});
    return this;
  },
  
  /**
   * Inserts the calendar into the element making it inlined
   *
   * @param Element element or String element id
   * @param String optional position top/bottom/before/after/instead, 'bottom' is default
   * @return Calendar this
   */
  insertTo: function(element, position) {
    this.element.addClass('right-calendar-inline').insertTo(element, position);
    return this;
  }
});

/**
 * This module handles the calendar elemnts building/updating processes
 *
 * Copyright (C) 2009 Nikolay V. Nemshilov aka St.
 */
Calendar.include({
  
// protected
  
  // updates the calendar view
  update: function(date) {
    var date = new Date(date || this.date);
    
    var monthes     = this.element.select('div.right-calendar-month');
    var monthes_num = monthes.length;
    
    for (var i=-(monthes_num - monthes_num/2).ceil()+1; i < (monthes_num - monthes_num/2).floor()+1; i++) {
      var month_date    = new Date(date);
      month_date.setMonth(date.getMonth() + i);
      
      this.updateMonth(monthes.shift(), month_date);
    }
    
    this.updateNextPrevMonthButtons(date, monthes_num);
    
    if (this.options.showTime) {
      this.hours.value = this.options.timePeriod < 60 ? date.getHours() :
        (date.getHours()/(this.options.timePeriod/60)).round() * (this.options.timePeriod/60);
      
      this.minutes.value = (date.getMinutes() / (this.options.timePeriod % 60)).round() * this.options.timePeriod;
    }
    
    return this;
  },
  
  // updates a single month-block with the given date
  updateMonth: function(element, date) {
    // getting the number of days in the month
    date.setDate(32);
    var days_number = 32 - date.getDate();
    date.setMonth(date.getMonth()-1);
    
    var cur_day = (this.date.getTime() / 86400000).ceil();
    
    // collecting the elements to update
    var rows  = element.select('tbody tr');
    var cells = rows.shift().select('td');
    element.select('tbody td').each(function(td) {
      td.innerHTML = '';
      td.className = 'right-calendar-day-blank';
    });
    
    for (var i=1; i <= days_number; i++) {
      date.setDate(i);
      var day_num = date.getDay();
      
      if (this.options.firstDay) {
        day_num = day_num ? day_num-1 : 6;
      }
      
      cells[day_num].innerHTML = ''+i;
      cells[day_num].className = cur_day == (date.getTime() / 86400000).ceil() ? 'right-calendar-day-selected' : '';
      
      if ((this.options.minDate && this.options.minDate > date) || (this.options.maxDate && this.options.maxDate < date))
        cells[day_num].className = 'right-calendar-day-disabled';
        
      cells[day_num].date = new Date(date);
      
      if (day_num == 6) {
        cells = rows.shift().select('td');
      }
    }
    
    element.first('div.right-calendar-month-caption').update(this.options.i18n.monthNames[date.getMonth()]+" "+date.getFullYear());
  },
  
  updateNextPrevMonthButtons: function(date, monthes_num) {
    if (this.options.minDate) {
      var beginning = new Date(date.getFullYear(),0,1,0,0,0);
      beginning.setMonth(date.getMonth() - (monthes_num - monthes_num/2).ceil());
      
      var min_date = new Date(this.options.minDate.getFullYear(), this.options.minDate.getMonth(), 1, 0,0,0);
      
      this.hasPrevMonth = beginning >= min_date;
    } else {
      this.hasPrevMonth = true;
    }
    
    if (this.options.maxDate) {
      var end = new Date(date);
      var max_date = new Date(this.options.maxDate);
      [end, max_date].each(function(date) {
        date.setDate(32);
        date.setMonth(date.getMonth() - 1);
        date.setDate(32 - date.getDate());
        date.setHours(0);
        date.setMinutes(0);
        date.setSeconds(0);
        date.setMilliseconds(0);
      });
      
      this.hasNextMonth = end < max_date;
    } else {
      this.hasNextMonth = true;
    }
    
    this.nextButton[this.hasNextMonth ? 'removeClass':'addClass']('right-ui-button-disabled');
    this.prevButton[this.hasPrevMonth ? 'removeClass':'addClass']('right-ui-button-disabled');
  },

  // builds the calendar
  build: function() {
    this.buildSwaps();
    
    // building the calendars greed
    var greed = tbody = $E('table', {'class': 'right-calendar-greed'}).insertTo(this.element);
    if (Browser.OLD) tbody = $E('tbody').insertTo(greed);
    
    for (var y=0; y < this.options.numberOfMonths[1]; y++) {
      var row   = $E('tr').insertTo(tbody);
      for (var x=0; x < this.options.numberOfMonths[0]; x++) {
        $E('td').insertTo(row).insert(this.buildMonth());
      }
    }
    
    this.buildTime();
    this.buildButtons();
    
    return this;
  },
  
  // builds the monthes swapping buttons
  buildSwaps: function() {
    this.prevButton = $E('div', {'class': 'right-ui-button right-calendar-prev-button',
        html: '&lsaquo;', title: this.options.i18n.Prev}).insertTo(this.element);
    this.nextButton = $E('div', {'class': 'right-ui-button right-calendar-next-button',
        html: '&rsaquo;', title: this.options.i18n.Next}).insertTo(this.element);
  },
  
  // builds a month block
  buildMonth: function() {
    return $E('div', {'class': 'right-calendar-month'}).insert([
      $E('div', {'class': 'right-calendar-month-caption'}),
      $E('table').insert(
        '<thead><tr>'+
          this.options.dayNames.map(function(name) {return '<th>'+name+'</th>';}).join('')+
        '</tr></thead><tbody>'+
          '123456'.split('').map(function() {return '<tr><td><td><td><td><td><td><td></tr>'}).join('')+
        '</tbody>'
      )
    ]);
  },
  
  // builds the time selection block
  buildTime: function() {
    if (!this.options.showTime) return;
    
    this.hours = $E('select');
    this.minutes = $E('select');
    
    var minute_options_number = 60 / this.options.timePeriod;
    
    (minute_options_number == 0 ? 1 : minute_options_number).times(function(i) {
      i = i * this.options.timePeriod;
      var c = i < 10 ? '0'+i : i;
      this.minutes.insert($E('option', {value: i, html: c}));
    }, this);
    
    var hour_options_number = this.options.timePeriod > 59 ? (24 * 60 / this.options.timePeriod) : 24;
    
    (hour_options_number == 0 ? 1 : hour_options_number).times(function(i) {
      if (this.options.timePeriod > 59) i = (i * this.options.timePeriod / 60).floor();
      var c = i < 10 ? '0'+i : i;
      this.hours.insert($E('option', {value: i, html: c}));
    }, this);
    
    $E('div', {'class': 'right-calendar-time'}).insertTo(this.element)
      .insert([this.hours, document.createTextNode(":"), this.minutes]);
  },
  
  // builds the bottom buttons block
  buildButtons: function() {
    if (!this.options.showButtons) return;
    
    this.nowButton = $E('div', {'class': 'right-ui-button right-calendar-now-button', html: this.options.i18n.Now});
    this.doneButton = $E('div', {'class': 'right-ui-button right-calendar-done-button', html: this.options.i18n.Done});
    
    $E('div', {'class': 'right-ui-buttons right-calendar-buttons'})
      .insert([this.doneButton, this.nowButton]).insertTo(this.element);
  }

});

/**
 * This module handles the events connection
 *
 * Copyright (C) 2009 Nikolay V. Nemshilov aka St.
 */
Calendar.include({
  /**
   * Initiates the 'select' event on the object
   *
   * @param Date date
   * @return Calendar this
   */
  select: function(date) {
    this.date = date;
    return this.fire('select', date);
  },
  
  /**
   * Covers the 'done' event fire
   *
   * @return Calendar this
   */
  done: function() {
    if (!this.element.hasClass('right-calendar-inline'))
      this.hide();
    return this.fire('done', this.date);
  },
  
  /**
   * Switches to one month forward
   *
   * @return Calendar this
   */
  next: function() {
    this.prevDate = new Date(this.prevDate || this.date);
    
    if (this.hasNextMonth) {
      this.prevDate.setMonth(this.prevDate.getMonth() + 1);
    }
    return this.update(this.prevDate);
  },
  
  /**
   * Switches to on month back
   *
   * @return Calendar this
   */
  prev: function() {
    this.prevDate = new Date(this.prevDate || this.date);
    
    if (this.hasPrevMonth) {
      this.prevDate.setMonth(this.prevDate.getMonth() - 1);
    }
    return this.update(this.prevDate);
  },
// protected
  
  connectEvents: function() {
    // connecting the monthes swapping
    this.prevButton.onClick(this.prev.bind(this));
    this.nextButton.onClick(this.next.bind(this));
    
    // connecting the calendar day-cells
    this.element.select('div.right-calendar-month table tbody td').each(function(cell) {
      cell.onClick(function() {
        if (cell.innerHTML != '') {
          var prev = this.element.first('.right-calendar-day-selected');
          if (prev) prev.removeClass('right-calendar-day-selected');
          cell.addClass('right-calendar-day-selected');
          this.setDay(cell.date);
        }
      }.bind(this));
    }, this);
    
    // connecting the time picker events
    if (this.hours) {
      this.hours.on('change', this.setTime.bind(this));
      this.minutes.on('change', this.setTime.bind(this));
    }
    
    // connecting the bottom buttons
    if (this.nowButton) {
      this.nowButton.onClick(this.setDate.bind(this, new Date()));
      this.doneButton.onClick(this.done.bind(this));
    }
    
    // blocking all the events from the element
    this.element.onClick(function(e) {e.stop();});
    
    return this;
  },
  
  // sets the date without nucking the time
  setDay: function(date) {
    this.date.setYear(date.getFullYear());
    this.date.setMonth(date.getMonth());
    this.date.setDate(date.getDate());
    return this.select(this.date);
  },
  
  setTime: function() {
    this.date.setHours(this.hours.value);
    this.date.setMinutes(this.minutes.value);
    return this.select(this.date);
  }
  
});

/**
 * This module handles the calendar assignment to an input field
 *
 * Copyright (C) 2009 Nikolay V. Nemshilov aka St.
 */
Calendar.include({
  /**
   * Assigns the calendar to serve the given input element
   *
   * If no trigger element specified, then the calendar will
   * appear and disappear with the element haveing its focus
   *
   * If a trigger element is specified, then the calendar will
   * appear/disappear only by clicking on the trigger element
   *
   * @param Element input field
   * @param Element optional trigger
   * @return Calendar this
   */
  assignTo: function(input, trigger) {
    var input = $(input), trigger = $(trigger);
    
    if (trigger) {
      trigger.onClick(function(e) {
        e.stop();
        this.showAt(input.focus());
      }.bind(this));
    } else {
      input.on({
        focus: this.showAt.bind(this, input),
        click: function(e) { e.stop(); },
        keyDown: function(e) {
          if (e.keyCode == 9 && this.element.visible())
            this.hide();
        }.bind(this)
      });
    }
    
    document.onClick(this.hide.bind(this));
    
    return this;
  },
  
  /**
   * Shows the calendar at the given element left-bottom corner
   *
   * @param Element element or String element id
   * @return Calendar this
   */
  showAt: function(element) {
    var element = $(element), dims = element.dimensions();
    this.setDate(this.parse(element.value));
    
    // RightJS < 1.4.1 bug handling
    if (RightJS.version < '1.4.1') {
      if (Browser.WebKit) {
        dims.left += document.body.scrolls().x;
        dims.top  += document.body.scrolls().y;
      } else if (Browser.Konqueror) {
        dims.left = element.offsetLeft;
        dims.top  = element.offsetTop;
      }
    }
    
    this.element.setStyle({
      position: 'absolute',
      margin: '0',
      left: (dims.left)+'px',
      top: (dims.top + dims.height)+'px'
    }).insertTo(document.body);
    
    this.stopObserving('select').stopObserving('done');
    this.on(this.doneButton ? 'done' : 'select', function() {
      element.value = this.format();
    }.bind(this));
      
    return this.hideOthers().show();
  },
  
  /**
   * Toggles the calendar state at the associated element position
   *
   * @param Element input
   * @return Calendar this
   */
  toggleAt: function(input) {
    if (this.element.parentNode && this.element.visible()) {
      this.hide();
    } else {
      this.showAt(input);
    }
    return this;
  },
  
// protected

  // hides all the other calendars on the page
  hideOthers: function() {
    $$('div.right-calendar').each(function(element) {
      if (!element.hasClass('right-calendar-inline')) {
        if (element != this.element) {
          element.hide();
        }
      }
    });
    
    return this;
  }
});

/**
 * This module handles the dates parsing/formatting processes
 *
 * To format dates and times this scripts use the GNU (C/Python/Ruby) strftime
 * function formatting principles
 *
 *   %a - The abbreviated weekday name (``Sun'')
 *   %A - The  full  weekday  name (``Sunday'')
 *   %b - The abbreviated month name (``Jan'')
 *   %B - The  full  month  name (``January'')
 *   %d - Day of the month (01..31)
 *   %e - Day of the month without leading zero (1..31)
 *   %m - Month of the year (01..12)
 *   %y - Year without a century (00..99)
 *   %Y - Year with century
 *   %H - Hour of the day, 24-hour clock (00..23)
 *   %k - Hour of the day, 24-hour clock without leading zero (0..23)
 *   %I - Hour of the day, 12-hour clock (01..12)
 *   %l - Hour of the day, 12-hour clock without leading zer (0..12)
 *   %p - Meridian indicator (``AM''  or  ``PM'')
 *   %P - Meridian indicator (``pm''  or  ``pm'')
 *   %M - Minute of the hour (00..59)
 *   %S - Second of the minute (00..60)
 *   %% - Literal ``%'' character
 *
 * Copyright (C) 2009 Nikolay V. Nemshilov aka St.
 */
Calendar.include({
  /**
   * Parses out the given string based on the current date formatting
   *
   * @param String string date
   * @return Date parsed date or null if it wasn't parsed
   */
  parse: function(string) {
    var date;
    
    if (string instanceof Date || Date.parse(string)) {
      date = new Date(string);
      
    } else if (isString(string) && string) {
      var tpl = RegExp.escape(this.options.format);
      var holders = tpl.match(/%[a-z]/ig).map('match', /[a-z]$/i).map('first').without('%');
      var re  = new RegExp('^'+tpl.replace(/%p/i, '(pm|PM|am|AM)').replace(/(%[a-z])/ig, '(.+?)')+'$');
      
      var match = string.trim().match(re);
      
      if (match) {
        match.shift();
        
        var year = null, month = null, date = null, hour = null, minute = null, second = null, meridian;
        
        while (match.length) {
          var value = match.shift();
          var key   = holders.shift();
          
          if (key.toLowerCase() == 'b') {
            month = this.options.i18n[key=='b' ? 'monthNamesShort' : 'monthNames'].indexOf(value);
          } else if (key.toLowerCase() == 'p') {
            meridian = value.toLowerCase();
          } else {
            value = value.toInt();
            switch(key) {
              case 'd': 
              case 'e': date   = value; break;
              case 'm': month  = value-1; break;
              case 'y': 
              case 'Y': year   = value; break;
              case 'H': 
              case 'k': 
              case 'I': 
              case 'l': hour   = value; break;
              case 'M': minute = value; break;
              case 'S': second = value; break;
            }
          }
        }
        
        // converting 1..12am|pm into 0..23 hours marker
        if (meridian) {
          hour = hour == 12 ? 0 : hour;
          hour = (meridian == 'pm' ? hour + 12 : hour);
        }
        
        date = new Date(year, month, date, hour, minute, second);
      }
    } else {
      date = new Date();
    }
    
    return date;
  },  
  
  /**
   * Formats the current date into a string depend on the current or given format
   *
   * @param String optional format
   * @return String formatted data
   */
  format: function(format) {
    var i18n   = this.options.i18n;
    var day    = this.date.getDay();
    var month  = this.date.getMonth();
    var date   = this.date.getDate();
    var year   = this.date.getFullYear();
    var hour   = this.date.getHours();
    var minute = this.date.getMinutes();
    var second = this.date.getSeconds();
    
    var hour_ampm = (hour == 0 ? 12 : hour < 13 ? hour : hour - 12);
    
    var values    = {
      a: i18n.dayNamesShort[day],
      A: i18n.dayNames[day],
      b: i18n.monthNamesShort[month],
      B: i18n.monthNames[month],
      d: (date < 10 ? '0' : '') + date,
      e: ''+date,
      m: (month < 9 ? '0' : '') + (month+1),
      y: (''+year).substring(2,4),
      Y: ''+year,
      H: (hour < 10 ? '0' : '')+ hour,
      k: '' + hour,
      I: (hour > 0 && (hour < 10 || (hour > 12 && hour < 22)) ? '0' : '') + hour_ampm,
      l: '' + hour_ampm,
      p: hour < 12 ? 'AM' : 'PM',
      P: hour < 12 ? 'am' : 'pm',
      M: (minute < 10 ? '0':'')+minute,
      S: (second < 10 ? '0':'')+second,
      '%': '%'
    };
    
    var result = format || this.options.format;
    for (var key in values) {
      result = result.replace('%'+key, values[key]);
    }
    
    return result;
  }
});

/**
 * Calendar fields autodiscovery via the rel="calendar" attribute
 *
 * Copyright (C) 2009 Nikolay V. Nemshilov aka St.
 */
document.onReady(function() {
  var calendar = new Calendar();
  var rel_id_re = new RegExp(Calendar.Options.relName+'\\[(.+?)\\]');
  
  $$(Calendar.Options.checkTags+'[rel*='+Calendar.Options.relName+']').each(function(element) {
    var rel_id = element.get('rel').match(rel_id_re);
    if (rel_id) {
      var input = $(rel_id[1]);
      if (input) {
        calendar.assignTo(input, element);
      }
    } else {
      calendar.assignTo(element);
    }
  });
});


document.write("<style type=\"text/css\">*.right-ui-button{display:inline-block;*display:inline;*zoom:1;height:1em;line-height:1em;padding:.2em .5em;text-align:center;border:1px solid #CCC;border-radius:.2em;-moz-border-radius:.2em;-webkit-border-radius:.2em;cursor:pointer;color:#555;background-color:#FFF}*.right-ui-button:hover{color:#222;border-color:#BA8;background-color:#FB6}*.right-ui-button-disabled,*.right-ui-button-disabled:hover{color:#888;background:#EEE;border-color:#CCC;cursor:default}*.right-ui-buttons{margin-top:.5em}div.right-calendar{position:absolute;height:auto;border:1px solid #BBB;position:relative;padding:.5em;border-radius:.3em;-moz-border-radius:.3em;-webkit-border-radius:.3em;cursor:default;background-color:#EEE;-moz-box-shadow:.2em .4em .8em #666;-webkit-box-shadow:.2em .4em .8em #666}div.right-calendar-inline{position:relative;display:inline-block;*display:inline;*zoom:1;-moz-box-shadow:none;-webkit-box-shadow:none}div.right-calendar-prev-button,div.right-calendar-next-button{position:absolute;float:left;width:1em;padding:.15em .4em}div.right-calendar-next-button{right:.5em}div.right-calendar-month-caption{text-align:center;height:1.2em;line-height:1.2em}table.right-calendar-greed{border-spacing:0px;border:none;background:none;width:auto}table.right-calendar-greed td{vertical-align:top;border:none;background:none;margin:0;padding:0;padding-right:.4em}table.right-calendar-greed td:last-child{padding:0}div.right-calendar-month table{margin:0;padding:0;border:none;width:auto;margin-top:.2em;border-spacing:1px;border-collapse:separate;border:none;background:none}div.right-calendar-month table th{color:#777;text-align:center;border:none;background:none;padding:0;margin:0}div.right-calendar-month table td,div.right-calendar-month table td:last-child{text-align:right;padding:.1em .3em;background-color:#FFF;border:1px solid #CCC;cursor:pointer;border-radius:.2em;-moz-border-radius:.2em;-webkit-border-radius:.2em}div.right-calendar-month table td:hover{background-color:#FB6;border-color:#BA8}div.right-calendar-month table td.right-calendar-day-blank{background:transparent;cursor:default;border:none}div.right-calendar-month table td.right-calendar-day-selected{background-color:#FB6;border-color:#BA8;color:brown}div.right-calendar-month table td.right-calendar-day-disabled{color:#888;background:#EEE;border-color:#CCC;cursor:default}div.right-calendar-time{text-align:center}div.right-calendar-time select{margin:0 .4em}div.right-calendar-buttons div.right-ui-button{width:3.2em}div.right-calendar-done-button{position:absolute;right:.5em}</style>");