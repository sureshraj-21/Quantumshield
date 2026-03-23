const fs = require('fs');
const parser = require('@babel/parser');
const orig = fs.readFileSync('src/App.js','utf8');
const lines = orig.split('\n');
const start = 1155;
const end = 1165;
const candidates = [
  ['A','  </div>\n  )}\n  </div>\n  </div>\n  </div>\n);'],
  ['B','  </div>\n  )}\n  </div>\n  </div>\n);'],
  ['C','  </div>\n  )}\n  </div>\n);'],
  ['D','  </div>\n  )}\n</div>\n);'],
  ['E','  </div>\n  )}\n  </div>\n  </div>\n  </div>\n  </div>\n);'],
  ['F','  </div>\n  )}\n  </div>\n  </div>\n  </div>\n  </div>\n  </div>\n);']
];
for (const [name, replacement] of candidates) {
  const m = lines.slice(0, start-1).concat(replacement.split('\n')).concat(lines.slice(end));
  const text = m.join('\n');
  try {
    parser.parse(text,{sourceType:'module', plugins:['jsx']});
    console.log('OK', name);
    return;
  } catch (e) {
    console.log('ERR', name, e.message);
  }
}
