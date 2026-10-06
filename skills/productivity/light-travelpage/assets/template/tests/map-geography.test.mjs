import test from 'node:test';
import assert from 'node:assert/strict';
import { copyFileSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { Window } from 'happy-dom';

test('mobile map zoom starts at the configured itinerary inset', (t) => {
  const window = new Window({ url: 'http://localhost/' });
  t.after(() => window.happyDOM.abort());
  window.eval(readFileSync(new URL('../route-ui.js', import.meta.url), 'utf8') + '\nwindow.mapZoomScrollLeftForTest = mapZoomScrollLeft;');
  const region = { canvas: { width: 1448 }, projection: { frame: { x: 1000, width: 300 } } };
  const offset = window.mapZoomScrollLeftForTest(region, 1100, 350, true);
  assert.ok(offset > 650 && offset < 750, `right-side inset should be visible; got ${offset}`);
  assert.equal(window.mapZoomScrollLeftForTest(region, 1100, 350, false), 375);
});

test('geographic map builds a sourced outline and keeps coordinates fixed', (t) => {
  const root = mkdtempSync(path.join(tmpdir(), 'travel-geography-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(path.join(root, 'scripts'), { recursive: true });
  mkdirSync(path.join(root, 'assets/maps/templates'), { recursive: true });
  copyFileSync(new URL('../scripts/build-map.mjs', import.meta.url), path.join(root, 'scripts/build-map.mjs'));
  writeFileSync(path.join(root, 'package.json'), '{"type":"module"}\n');
  writeFileSync(path.join(root, 'assets/maps/templates/manifest.json'), '{"templates":[],"disclaimer":"fixture"}\n');
  writeFileSync(path.join(root, 'assets/maps/test-coast.geojson'), JSON.stringify({
    type: 'Feature', geometry: { type: 'MultiPolygon', coordinates: [[[[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]]] }
  }));
  const trip = {
    metadata: { assets: {} }, config: { modules: { overview: true } }, trip: {},
    map: {
      mapMode: 'geographic-outline',
      disclaimer: '本图仅表达地点的相对方位与路线顺序，不代表真实比例或精确地理边界。',
      region: { id: 'test', label: 'Test', countryCode: 'JP', geographic: {
        outlineFile: 'assets/maps/test-coast.geojson', baseImage: 'assets/maps/test-coast.svg',
        mainBounds: [0, 0, 2, 2], mainFrame: { x: 600, y: 100, width: 700, height: 800 },
        detailBounds: [0, 0, 2, 2], detailFrame: { x: 50, y: 600, width: 500, height: 400 }
      } },
      places: [
        { id: 'a', name: 'A', countryCode: 'JP', geo: { lat: .5, lng: .5 } },
        { id: 'b', name: 'B', countryCode: 'JP', geo: { lat: 1.5, lng: 1.5 } }
      ],
      routes: [{ day: 1, placeIds: ['a', 'b'] }]
    }
  };
  const tripPath = path.join(root, 'trip-data.json');
  const build = () => spawnSync(process.execPath, ['scripts/build-map.mjs'], { cwd: root, encoding: 'utf8' });
  writeFileSync(tripPath, JSON.stringify(trip));
  const positive = build();
  assert.equal(positive.status, 0, positive.stderr);
  const result = JSON.parse(readFileSync(tripPath, 'utf8')).routeMap.regions[0];
  assert.equal(result.mapMode, 'geographic-inset');
  assert.match(result.disclaimer, /地理轮廓来自配置的边界数据/);
  assert.doesNotMatch(result.disclaimer, /不代表真实比例或精确地理边界/);
  assert.match(result.description, /地理轮廓与行程地点/);
  assert.ok(result.places[0].x < result.places[1].x);
  assert.ok(result.places[0].y > result.places[1].y);
  assert.match(readFileSync(path.join(root, result.baseImage), 'utf8'), /<path d="M/);

  trip.map.region.geographic.detailBounds = [0, 0, 1, 1];
  writeFileSync(tripPath, JSON.stringify(trip));
  const negative = build();
  assert.notEqual(negative.status, 0);
  assert.match(negative.stderr, /outside detail bounds/);
});
